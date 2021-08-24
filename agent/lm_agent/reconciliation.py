#!/usr/bin/env python3
"""
Reconciliation functionality live here.
"""
import asyncio
from typing import Dict, List

from fastapi import HTTPException, status
from httpx import ConnectError

from lm_agent.forward import async_client
from lm_agent.logs import logger
from lm_agent.tokenstat import report
from lm_agent.workload_managers.slurm.cmd_utils import return_formatted_squeue_out, squeue_parser

RECONCILE_URL_PATH = "/api/v1/license/reconcile"


async def remove_booked_for_job_id(job_id: str):
    """
    Send DELETE to /api/v1/booking/book/{job_id}.
    """
    response = await async_client().delete(f"/api/v1/booking/book/{job_id}")
    if response.status_code != status.HTTP_200_OK:
        logger.error(f"{job_id} could not be deleted.")
        logger.debug(f"response from delete: {response.__dict__}")


async def get_all_grace_times() -> Dict[int, int]:
    """
    Send GET to /api/v1/config/all.
    """
    response = await async_client().get("/api/v1/config/all")
    configs = response.json()
    grace_times = {config["id"]: config["grace_time"] for config in configs}
    return grace_times


async def get_booked_for_job_id(job_id: str) -> Dict:
    """
    Return the booking row for the given job_id.
    """
    response = await async_client().get(f"/api/v1/booking/job/{job_id}")
    return response.json()


def get_greatest_grace_time(job_id: str, grace_times: Dict[int, int], booking_rows: List) -> int:
    """
    Find the greatest grace_time for the given job_id.
    """
    greatest_grace_time = -1
    for book in booking_rows:
        if not book:
            continue
        for inner_book in book:
            if str(inner_book["job_id"]) != str(job_id):
                continue
            config_id_for_grace_times = inner_book["config_id"]
            greatest_grace_time = max(greatest_grace_time, grace_times[config_id_for_grace_times])
    return greatest_grace_time


def get_running_jobs(squeue_result: List) -> List:
    return [j for j in squeue_result if j["state"] == "RUNNING"]


async def clean_booked_grace_time():
    """
    Clean the booked licenses if the job's running time is greater than the grace_time.
    """
    formatted_squeue_output = return_formatted_squeue_out()
    if not formatted_squeue_output:
        return
    squeue_result = squeue_parser(formatted_squeue_output)
    squeue_running_jobs = get_running_jobs(squeue_result)

    grace_times = await get_all_grace_times()
    get_booked_call = []
    for job in squeue_running_jobs:
        job_id = job["job_id"]
        get_booked_call.append(get_booked_for_job_id(job_id))

    booking_rows_for_running_jobs = await asyncio.gather(*get_booked_call)

    # get the greatest grace_time for each job
    for job in squeue_running_jobs:
        job_id = job["job_id"]
        greatest_grace_time = get_greatest_grace_time(job_id, grace_times, booking_rows_for_running_jobs)
        # if the running_time is greater than the greatest grace_time, delete the booking for it
        if job["run_time_in_seconds"] > greatest_grace_time and greatest_grace_time != -1:
            await remove_booked_for_job_id(job_id)


async def reconcile():
    """Generate the report and reconcile the license feature token usage."""
    # Generate the report.
    logger.info("Beginning forced reconciliation process")
    rep = await report()
    if not rep:
        logger.error(
            "No license data could be collected, check that tools are installed "
            "correctly and the right hosts/ports are configured in settings"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="report failed",
        )
    # Clean booked using grace_time
    await clean_booked_grace_time()
    # Send the report to the backend.
    client = async_client()
    path = RECONCILE_URL_PATH
    try:
        r = await client.patch(path, json=rep)
    except ConnectError as e:
        logger.error(f"{client.base_url}{path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="connection to reconcile api failed",
        )

    if r.status_code != status.HTTP_200_OK:
        logger.error(f"{r.url}: {r.status_code}!: {r.text}")
        raise HTTPException(
            status_code=r.status_code,
            detail="reconciliation failed",
        )

    logger.info(f"Forced reconciliation succeeded. backend updated: {len(rep)} feature(s)")
    return r

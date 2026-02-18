from fastapi import FastAPI, Query
from rq.job import Job
from client.rq_client import queue
from queues.worker import process_query
app = FastAPI()

@app.get("/")
def root():
    return {"status": "Server is running"}

@app.post("/chat")
def chat_route(
    query: str = Query(..., description="The query from the user.")
):
    job = queue.enqueue(process_query, query)

    return {"status": "queued", "job_id": job.id}

@app.get("/job-status")
def get_result(
        job_id: str = Query(..., description="Job ID")
):
    job = Job.fetch(job_id, connection=queue.connection)
    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result,
        "error": job.exc_info,
    }
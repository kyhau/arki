from boto3.session import Session
from botocore.exceptions import ClientError
import click
import logging
from os.path import join
from os import walk
import time

logging.getLogger().setLevel(logging.DEBUG)


def read_sql(filename):
    with open(filename, "r") as sql_file:
        content = sql_file.read()
    return content.replace("\n", " ").replace(";", "")


def get_sql_files(root_dir):
    sql_files = []
    for root, dir, files in walk(root_dir):
        sql_files.extend(join(root, file) for file in files if file.endswith(".sql"))
    return sql_files


def athena_to_s3(session, region, database, sqlfile, output, max_execution=60):
    client = session.client("athena", region_name=region)
    
    execution = client.start_query_execution(
        QueryString=read_sql(sqlfile),
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output}
    )
    execution_id = execution["QueryExecutionId"]
    state = "RUNNING"
    
    while max_execution > 0 and state in ["RUNNING"]:
        max_execution = max_execution - 1
        response = client.get_query_execution(QueryExecutionId=execution_id)
        
        if "QueryExecution" in response and \
                "Status" in response["QueryExecution"] and \
                "State" in response["QueryExecution"]["Status"]:
            state = response["QueryExecution"]["Status"]["State"]
            if state == "SUCCEEDED":
                s3_path = response["QueryExecution"]["ResultConfiguration"]["OutputLocation"]
                print("Execution Result: {} {}".format(state, response["QueryExecution"]["ResultConfiguration"]["OutputLocation"]))
            elif state == "RUNNING":
                time.sleep(1)
        else:
            logging.error("Unable to get_query_execution")


@click.command()
@click.option("--profile", "-p", help="AWS profile name.", default="default")
@click.option("--region", "-r", help="AWS Region; use 'all' for all regions.", default="ap-southeast-2")
@click.option("--database", "-d", help="Database name.", required=True)
@click.option("--sqldir", help="Directory containing .sql files")
@click.option("--sqlfile", help="File containing a SQL statement.")
@click.option("--workgroup", "-w", help="Athena Workgroup name")
@click.option("--output", "-o", help="S3 output location: e.g. s3://path/to/query/bucket/", required=True)
def main(profile, region, database, sqlfile, output):
    try:
        session = Session(profile_name=profile)
        athena_to_s3(session, region, database, sqlfile, output)
    
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["AuthFailure", "ExpiredToken", "InvalidClientTokenId", "AccessDeniedException"]:
            logging.error(f"{profile} {error_code}. Skipped")
        else:
            raise


if __name__ == "__main__":
    main()

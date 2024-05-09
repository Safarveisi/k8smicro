# Analysing s3 persisted dill files
A web application (based on FastAPI) running on Kubernetes that receives
requests for a specific month and day in 2024, gathers dill files 
belonging to the requested time from a S3 bucket, converts them into
a pandas dataframe, and counts the number of rows whose `failed_attrs != "empty"`.
If there are not any dill files for the requsted time, it returns a proper messsage
to the user. 

### Usage
| **File/Dir** | **Desc** |
| --- | --- |
| `k8smicro` | Directory containing the application source files. </br> `k8smicro/web` contains the source file for the web application and `k8smicro/caller` contains the source file of the client that sends HTTP requests to the web application |
| `microservice` | Source code for the app |
| `Dockerfile` | Instructions to create the docker image of the web application and the client |
| `build-image.sh` | Facilitates building the docker images for the web application and the client. </br> A build argument (`ARG role` in the `Dockerfile`) is used to distinguish between the two components while building the images |
| `deploy.sh` | Facilitates deploying/removing the service into/from the Kubernetes cluster (use `apply` or `delete` as its argument) |
| `kube-deploy.yaml` | Kubernetes manifest file |

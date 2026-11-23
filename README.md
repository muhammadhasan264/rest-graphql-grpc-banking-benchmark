# rest-graphql-grpc-banking-benchmark
Python benchmark comparing payload size and local latency of REST (FastAPI), GraphQL-style responses and gRPC (Protobuf) on a sample banking transaction, with a hybrid architecture diagram for internal and external bank APIs.

# REST vs GraphQL vs gRPC in Banking: Payload and Latency Benchmark

Companion code for my article on FinTech Bulletins: [link once published].

## What it measures
Payload size and local latency for one sample payment transaction
served over REST (FastAPI), GraphQL-style response (3 fields vs all), and gRPC (Protobuf).

## Results (my machine)
| Metric | REST | GraphQL | gRPC |
|---|---|---|---|
| Payload (bytes) | 207 | 100 / 232 | 118 |
| Median latency (ms) | your value | your value | your value |

![Architecture](images/architecture.png)

## Run it
pip install -r requirements.txt
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. txn.proto
python bench.py

## Limitations
Local single-machine test, no network or TLS. The GraphQL case simulates
a field-selected response and does not use a full GraphQL server.

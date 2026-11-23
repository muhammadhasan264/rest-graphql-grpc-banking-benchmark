import json, statistics, time, threading
from concurrent import futures
import grpc, httpx, uvicorn, txn_pb2, txn_pb2_grpc
from fastapi import FastAPI

T = dict(transactionId="TXN20261123000123", fromAccount="PK36SCBL0000001123456702",
         toAccount="PK24HABB0000009876543210", amount=25000.50, currency="PKR",
         timestamp="2026-11-23T10:15:30Z", status="COMPLETED")
pb = txn_pb2.Transaction(transaction_id=T["transactionId"], from_account=T["fromAccount"],
     to_account=T["toAccount"], amount=T["amount"], currency=T["currency"],
     timestamp=T["timestamp"], status=T["status"])
json_b = len(json.dumps(T, separators=(",",":")).encode())
pb_b = len(pb.SerializeToString())
# GraphQL: client asks only 3 fields
gql_resp = {"data":{"transaction":{k:T[k] for k in ("transactionId","amount","status")}}}
gql_b = len(json.dumps(gql_resp, separators=(",",":")).encode())
gql_full = len(json.dumps({"data":{"transaction":T}}, separators=(",",":")).encode())
print("JSON",json_b,"PB",pb_b,"GQL3",gql_b,"GQLfull",gql_full)

app = FastAPI()
@app.get("/txn")
def g(): return T
@app.post("/graphql")
def gq(): return gql_resp
threading.Thread(target=lambda: uvicorn.run(app,host="127.0.0.1",port=8765,log_level="error"),daemon=True).start()

class S(txn_pb2_grpc.TxnServiceServicer):
    def GetTransaction(self, r, c): return pb
srv = grpc.server(futures.ThreadPoolExecutor(4))
txn_pb2_grpc.add_TxnServiceServicer_to_server(S(), srv)
srv.add_insecure_port("127.0.0.1:50551"); srv.start()
time.sleep(1.5)

N=1000
def run(f):
    for _ in range(100): f()
    t=[]
    for _ in range(N):
        s=time.perf_counter(); f(); t.append((time.perf_counter()-s)*1000)
    return statistics.median(t), sorted(t)[int(.95*N)]
with httpx.Client() as c:
    r=run(lambda: c.get("http://127.0.0.1:8765/txn"))
    q=run(lambda: c.post("http://127.0.0.1:8765/graphql",json={"query":"{transaction{transactionId amount status}}"}))
ch=grpc.insecure_channel("127.0.0.1:50551"); stub=txn_pb2_grpc.TxnServiceStub(ch)
g_=run(lambda: stub.GetTransaction(txn_pb2.TxnRequest(transaction_id="x")))
print("REST median/p95",r); print("GQL",q); print("gRPC",g_)

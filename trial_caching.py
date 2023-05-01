import ray
import time

ray.init(namespace="serve")

a = ray.get_actor(namespace="serve", name="CachingModelActor")

st = time.time()
ref = a.act.remote(name="Rajiv1")
result = ray.get(ref)
print(result)
print(f"Time1:{time.time() - st}")

st = time.time()
ref = a.act.remote(name="Rajiv2")
result = ray.get(ref)
print(result)
print(f"Time2:{time.time() - st}")

# This should return quickly
st = time.time()
ref = a.act.remote(name="Rajiv1")
result = ray.get(ref)
print(result)
print(f"Time1:{time.time() - st}")



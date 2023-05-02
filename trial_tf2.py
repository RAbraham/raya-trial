import ray

ray.init(namespace="serve")

a2 = ray.get_actor(namespace="serve", name="TF2Actor")

ref = a2.do.remote(name="Rajiv")
result = ray.get(ref)
print(result)

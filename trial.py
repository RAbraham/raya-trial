import ray

ray.init(namespace="serve")

a1 = ray.get_actor(namespace="serve", name="TF1Actor")
a2 = ray.get_actor(namespace="serve", name="TF2Actor")

ref = a1.act.remote(name="Rajiv")
result = ray.get(ref)
print(result)

ref = a2.do.remote(name="Rajiv")
result = ray.get(ref)
print(result)

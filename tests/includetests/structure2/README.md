This structure contains a mesh of includes (via path all other)
d1 includes d2,d3
d2 includes d3,d1
d3 includes d1,d2

Each dir pretends to be a separate, unrelated, project
No matter which dir you run t from, we should have access to all tasks,

d4 is unrelated to d1-3, it's used for one specific subset of tests



from YoungLion import Matrix, Vector

transform = Matrix([[2, 0], [0, 3]])
point = Vector([4, 5])
print("Transformed:", transform.vector_mul(point).components)
print("Identity shape:", Matrix.identity(3).shape)

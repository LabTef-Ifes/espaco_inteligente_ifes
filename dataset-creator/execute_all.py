"""Arquivo para executar todos os scripts em OOP de uma vez só"""

from request_2d import Skeleton2D
from request_3d import Skeleton3D
from export_3d import Export3D

# Executa o script de requisição de dados 2D
skeleton2d = Skeleton2D()
skeleton2d.run()
# Executa o script de requisição de dados 3D
skeleton3d = Skeleton3D()
skeleton3d.run()
# Executa o script de exportação de dados 3D
export3d = Export3D()
export3d.run()



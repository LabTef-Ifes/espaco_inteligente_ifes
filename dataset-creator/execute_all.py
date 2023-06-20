"""Arquivo para executar todos os scripts em OOP de uma vez só"""

from request_2d import Skeleton2D
from request_3d import Skeleton3D
from export_3d import Export3D

class Execute:
    def __init__(self):
        
        # Executa o script de requisição de dados 2D
        self.skeleton2d = Skeleton2D()
        # Executa o script de requisição de dados 3D
        self.skeleton3d = Skeleton3D()
        # Executa o script de exportação de dados 3D
        self.export3d = Export3D()
    
    def run(self,skeleton2d = True, skeleton3d = True, export3d = True):
        if skeleton2d:
            self.skeleton2d.run()
        if skeleton3d:
            self.skeleton3d.run()
        if export3d:
            self.export3d.run()
    

if __name__ == "__main__":
    execute = Execute()
    execute.run(skeleton2d = False, 
                skeleton3d = True,
                export3d = True)
import shutil
import json
source_file = '0.json'
with open(source_file) as f:
	config = json.load(f)
	print(config)
	novo_fps = input("Insira o novo valor de fps:")
	while not novo_fps.isnumeric():
		print("Entrada inválida, insira um número inteiro válido")
		novo_fps = input("Insira o novo valor de fps:")
	novo_fps = int(novo_fps)
	config['initial_config']['sampling']['frequency'] = novo_fps

with open(source_file,'w+') as f:
	json.dump(config,f,indent = 2)
for c in range(1,4):
	shutil.copyfile(source_file,str(c)+'.json')

	

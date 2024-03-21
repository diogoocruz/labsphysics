from main import dados

data = dados(r"C:\Users\diogo\labsphysics\labsphysics\teste.xlsx")

#data.ajuste("U","I")
#data.residuos("U", "I")

data.adicionar("R",r"$\Omega$", "U*I")

#data.adicionar("R2","lol", "np.log(R)**2" )
print(data.df)
print(data)
#print(data.df)
#data.ajuste("U","I")
print(data.chave)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import math
import sympy as sp


class dados:
    def __init__(self, ficheiro) -> None:
        self.df = pd.read_excel(ficheiro)
        self.chave = {}
        for column in self.df.columns:
            name = column.split("-")
            self.df = self.df.rename(columns={column:name[0].strip()})
            unidade = name[1].strip() if len(name)>1 else None
            incerteza = name[2].strip() if len(name)>2 else None
            self.chave[name[0].strip()] = (self.df[name[0].strip()].values, unidade, float(incerteza) if incerteza!=None else None)            

    def ajuste(self, x, y, graficos=True, sumario=False):
        xx = x 
        yy = y
        x = self.df[x]
        y = self.df[y]
        
        # Calcular as incertezas
        incertezas = self.chave[y.name][2]  # Obter as incertezas da chave
        
        X = sm.add_constant(x)
        model = sm.OLS(y, X)
        results = model.fit()
        m = results.params[1]
        b = results.params[0]

        if graficos:
            labelx = f"{xx} ({self.chave[xx][1]})"
            labely = f"{yy} ({self.chave[yy][1]})"
            

            
            # Incluir barras de erro para indicar incertezas
            if incertezas is not None:
                plt.errorbar(x, y, yerr=incertezas, fmt='o', capsize=5, label="Dados Exp.")
            else:
                plt.plot(x, y, 'o', label="Dados Exp.")

            plt.plot(x, m*x + b, label="Ajuste Lin.")
            plt.legend()
            plt.xlabel(labelx)
            plt.ylabel(labely)
            plt.grid()
            plt.show()
        
        if sumario:
            table = pd.DataFrame()
            model = results
            # Adicionar resultados da análise de regressão à tabela
            table.loc[0, "analysis"] = "R-squared"
            table.loc[0, "result"] = model.rsquared
            table.loc[1, "analysis"] = "m"
            table.loc[1, "result"] = f"{results.params[1]} ± {results.bse[1]}"
            table.loc[2, "analysis"] = "b"
            table.loc[2, "result"] = f"{results.params[0]} ± {results.bse[0]}"
            table.loc[5, "analysis"] = "u(y)"
            table.loc[5, "result"] = model.mse_resid ** 0.5

            # Imprimir tabela
            print(table)
                    
        return results

    
    def residuos(self,x, y):

        aj = self.ajuste(x,y, graficos=False)
        labelx = f"{x} ({self.chave[x][1]})"
        x = self.df[x]
        plt.plot(x, aj.resid, 'o')
        plt.axhline(2*aj.mse_resid ** 0.5, color="red", label=r"$\pm 2\sigma$")
        plt.axhline(-2*aj.mse_resid ** 0.5, color="red")
        plt.xlabel(labelx)
        plt.grid()
        plt.ylabel("Resíduos")
        plt.legend()
        plt.show()


    def adicionar(self, nome, unidades, expressao):
        simbolos = {key: sp.Symbol(key) for key in self.chave.keys()}
        
        # Define symbols for uncertainty associated with each variable
        simbolos_incerteza = {f"u_{key}": sp.Symbol(f"u_{key}") for key in self.chave.keys()}
        
        expressao = expressao.replace("np", "sp")
        
                
        expressao_simbolica = eval(expressao, {"math": math, "np": np, "sp": sp}, {**simbolos, **simbolos_incerteza})
            
        derivadas_parciais = {key: expressao_simbolica.diff(simbolos[key]) for key in simbolos}
            
        incerteza = 0
        for key, value in derivadas_parciais.items():
            incerteza += (value * simbolos_incerteza[f"u_{key}"]) ** 2
            
        incerteza = sp.sqrt(incerteza)
        
        valores_simbolicos = expressao_simbolica.subs({simbolos[key]: self.chave[key][0] for key in simbolos})
        print(f"Incerteza de {nome}: {incerteza}")
        expressao = expressao.replace("sp","np")
        expressao_simbolica = eval(expressao, {"math": math, "np": np, "sp": sp}, {**simbolos, **simbolos_incerteza})
    
    # Define a function to calculate uncertainty based on symbolic expression
        incerteza_func = sp.lambdify(list(simbolos_incerteza.values()), expressao_simbolica)
        incertezas = [self.chave[key][2] for key in self.chave.keys()]

        incerteza_numerica = incerteza_func(*incertezas)
        valores_numericos = eval(expressao, {"math":math, "np":np}, {key: value[0] for key, value in self.chave.items()})

        self.df[nome] = valores_numericos
        self.chave[nome] = (valores_numericos, unidades, incerteza_numerica)

        return valores_numericos, valores_simbolicos, incerteza_numerica  # Retornar os valores numéricos, a expressão simbólica e os valores numéricos da incerteza


    def __str__(self) -> str:
        string_representation = ""
        for k in self.chave.keys():
            string_representation += f"{k} ({self.chave[k][1]})\n {self.chave[k][2]}\n"
        return string_representation

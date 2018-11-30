#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

import networkx as nx
import matplotlib.pyplot as plt
import os
import sys


INF = 9999999
parent = dict()
rank = dict()
arquivos = []
grafo = 0
arvore=0
custo=0
selectedBox=''
class Ui_MainWindow(object):
    def initialize(self):
        # Leitura e exibição do diretório de entrada
        caminhos = [os.path.join("entrada/", nome) for nome in os.listdir("entrada/")]
        arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
        #opcao = raw_input("\nInsira o número equivalente à opção do arquivo que deseja determinar como entrada: ")       
        return arquivos
    def gerargrafo(sef,arquivo_selecionado):
        # Inicia a leitura do grafo
        global grafo
        grafo = nx.Graph()
        arq = open(arquivo_selecionado)
        linha = arq.readline()
        vertices, arestas = linha.split()            # Recebe a quantidade de vértices e arestas
        linha = arq.readline()                      # Primeira flag -1
        cont = 0
        # Recebendo a posição e peso dos vértices
        for linha in arq:
            if len(linha.split()) < 3:
                break
            else:
                grafo.add_node(cont)
                pos_x, pos_y, peso = linha.split()
                grafo.node[cont]['pos'] = (int(pos_x), int(pos_y))
                grafo.node[cont]['weight'] = int(peso)
                cont += 1
        # Recebendo as arestas e seus pesos
        for linha in arq:
            v1, v2, peso = linha.split()
            grafo.add_edge(int(v1), int(v2), weight = int(peso))
            grafo[int(v1)][int(v2)]['added'] = False
        pos = nx.get_node_attributes(grafo, 'pos')
        nx.draw(grafo, pos, with_labels=True)
        plt.show()
        return grafo
    
    def prim(self):
        global grafo
        grafo_residual = grafo.copy()
        arvore = nx.Graph()
        arvore.add_node(0)
        v_add = [0]
        arestas_arvore = []
        custo = 0
        menor_aresta = []
        # Loop para construir a AGM
        while arvore.number_of_nodes() != grafo_residual.number_of_nodes():
            menor_custo = INF
            for vertice in v_add:
                vizinhos = list(grafo_residual.neighbors(vertice))
                for neighbor in range(grafo_residual.degree(vertice)):
                    if grafo_residual[vertice][vizinhos[neighbor]]['weight'] < menor_custo:
                        menor_custo = grafo_residual[vertice][vizinhos[neighbor]]['weight']
                        menor_aresta = ([vertice, vizinhos[neighbor]])
            arestas_arvore.append([menor_aresta[0], menor_aresta[1]])
            v_add.append(menor_aresta[1])
            grafo_residual.remove_edge(menor_aresta[0], menor_aresta[1])
            grafo[menor_aresta[0]][menor_aresta[1]]['added'] = True
            arvore.add_node(menor_aresta[1], weight=grafo_residual.node[menor_aresta[1]]['weight'])

        # Cria a AGM com a lista de arestas obtidas

        for i in range(len(arestas_arvore)):
            arvore.add_edge(arestas_arvore[i][0], arestas_arvore[i][1])

        custo = self.calculates_cost(arvore)
        #print "\nO custo da AGMI gerada pelo algoritmo de Prim é %d.\n" % custo

        return custo, arvore, grafo


    def calculates_cost(self,arvore):
        global grafo
        custo_parcial = 0;
        # Soma o custo dos vértices não-folhas da AGM
        for vertice in arvore.nodes():
            if arvore.degree(vertice) > 1:
                custo_parcial += grafo.node[vertice]['weight']
        # Soma o custo das arestas da AGM ao custo parcial anterior
        for aresta in arvore.edges():
            v1, v2 = aresta
            custo_parcial += grafo[v1][v2]['weight']

        return custo_parcial            


    def kruskal(self):
        global grafo
        peso=0
        arestas=[]
        for vertice in grafo.nodes():
            self.make_set(vertice)
            agm = set()
            edges = list(grafo.edges())
            edges.sort()
        arestas=[]
        for edge in edges:
            vertice1, vertice2 = edge
            edge = (grafo[vertice1][vertice2]['weight'],vertice1,vertice2)
            arestas.append(edge)
            arestas.sort()
        for aresta in arestas:
            pesosA,vertice1, vertice2 = aresta
            if self.find(vertice1) != self.find(vertice2):
                self.union(vertice1, vertice2)
                agm.add(aresta)
                peso += pesosA
        return peso,sorted(agm)


    def return_edges_Kruskal(self,mst):
        global grafo
        arvore = nx.Graph()
        new_mst=[]
        for node in grafo.nodes():
            arvore.add_node(node,weight=grafo.node[node]['weight'])
        for i in range(len(mst)):
            arvore.add_edge(mst[i][1], mst[i][2])
            grafo[mst[i][1]][mst[i][2]]['added'] = True
        for element in mst:
            new_mst.append([element[1],element[2]])
        custo = self.calculates_cost(arvore)
        #print "\nO custo da AGMI gerada pelo algoritmo de Kruskal é %d.\n" % custo
        return arvore,new_mst, custo


    def make_set(self,vertice):
        parent[vertice] = vertice
        rank[vertice] = 0


    def find(self,vertice):
        if parent[vertice] != vertice:
            parent[vertice] = self.find(parent[vertice])
        return parent[vertice]


    def union(self,vertice1, vertice2):
        root1 = self.find(vertice1)
        root2 = self.find(vertice2)
        if root1 != root2:
            if rank[root1] > rank[root2]:
                parent[root2] = root1
            else: 
                parent[root1] = root2
            if rank[root1] == rank[root2]:
                rank[root2] += 1


    def refinement_heuristic(self):
        global grafo
        global arvore
        global custo
        # Função que remolda a AGM de acordo com o a heurística
        for vertice in range(grafo.number_of_nodes()):
            vizinhos = list(grafo.neighbors(vertice))
            for neighbor in range(grafo.degree(vertice)):
                if (vertice != vizinhos[neighbor]) and (grafo.has_edge(vizinhos[neighbor], vertice)):
                    if grafo[vertice][vizinhos[neighbor]]['added'] == False:
                        arvore.add_edge(vertice, vizinhos[neighbor])
                    # Verifica se a árvore possui ciclo com a nova aresta inserida
                    aux = nx.cycle_basis(arvore)
                    ciclo = [zip(nodes,(nodes[1:]+nodes[:1])) for nodes in aux]      
                    nova_aresta = None            
                    if len(ciclo) > 0:
                        for aresta in ciclo[0]:  
                            if aresta != (vertice, vizinhos[neighbor]) or aresta != (vizinhos[neighbor], vertice):                   # Compara se a aresta em questão é a mesma que foi inserida
                                arvore.remove_edge(aresta[0], aresta[1])
                                custo_parcial = self.calculates_cost(arvore)
                                if custo_parcial < custo:
                                    custo = custo_parcial                       # Altera o custo se a AGM encontrada possuir menor custo
                                    nova_aresta = aresta
                                    arvore.add_edge(aresta[0], aresta[1])
                                else:
                                    arvore.add_edge(aresta[0], aresta[1])       # Devolve a aresta inserida, caso o custo encontrado for maior que o atual

                    if nova_aresta != None:
                        arvore.remove_edge(nova_aresta[0], nova_aresta[1])
                        grafo[vertice][vizinhos[neighbor]]['added'] = True
                        grafo[nova_aresta[0]][nova_aresta[1]]['added'] = False
                    elif grafo[vertice][vizinhos[neighbor]]['added'] == False:
                        arvore.remove_edge(vertice, vizinhos[neighbor])

        #print ("O custo da nova AGMI gerada pela heurística de refinamento é %d.\n" % custo)
        
        return arvore, custo
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        font = QtGui.QFont()
        font.setFamily("Uroob")
        font.setPointSize(11)
        MainWindow.setFont(font)
        MainWindow.setIconSize(QtCore.QSize(50, 50))
        self.selectedBox=None


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(130, 20, 561, 51))
        font = QtGui.QFont()
        font.setFamily("Purisa")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(210, 129, 141, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setScaledContents(False)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(-20, 80, 851, 20))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.line.setFont(font)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(350, 130, 231, 25))
        self.comboBox.setObjectName("comboBox")
        #INICIALIZA grafo A PARTIR DO ARQUIVO SELECIONADO
        arquivos = self.initialize()
        self.comboBox.addItems(arquivos)
        self.comboBox.activated[str].connect(self.onActivated)
        #FINAL INICIALIZAR grafo
        

        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(-40, 180, 851, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(-20, 530, 851, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(170, 550, 491, 17))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 20, 51, 51))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("tree1.png"))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(730, 20, 51, 61))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("tree2.png"))
        self.label_5.setObjectName("label_5")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(130, 290, 111, 81))
        self.pushButton_2.setText("")
        #CALL THE FUNCTION WHO'S CALCULATE THE FIRST PRIM AGMI
        self.pushButton_2.clicked.connect(self.primButton)
        #CALL THE FUNCTION WHO'S CALCULATE THE FIRST PRIM AGMI
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("prim.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setIconSize(QtCore.QSize(100, 100))
        self.pushButton_2.setObjectName("pushButton_2")
        

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(500, 290, 111, 81))
        self.pushButton_3.setText("")
        
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("kruskal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_3.setIconSize(QtCore.QSize(100, 100))
        self.pushButton_3.setObjectName("pushButton_3")
        #CALL THE FUNCTION WHO'S CALCULATE KRUSKAL AGMI
        self.pushButton_3.clicked.connect(self.kruskalButton)
        #CALL THE FUNCTION WHO'S CALCULATE KRUSKAL AGM

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(350, 290, 111, 81))
        self.pushButton_4.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("heuristica.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_4.setIcon(icon2)
        self.pushButton_4.setIconSize(QtCore.QSize(100, 100))
        self.pushButton_4.setObjectName("pushButton_4")
        #CALL THE FUNCTION WHO'S CALCULATE FINAL AGMI
        self.pushButton_4.clicked.connect(self.heuristica)
        #CALL THE FUNCTION WHO'S CALCULATE FINAL AGMI
        #CALL THE FUNCTION WHO'S RESET ALL THE GRAPH AND TREES TO GENERATE NEW TREES
        self.pushButton_reset = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_reset.setGeometry(QtCore.QRect(620, 290, 111, 81))
        self.pushButton_reset.setText("Reset Graph")
        self.pushButton_reset.clicked.connect(self.resetGraph)
        #CALL THE FUNCTION WHO'S RESET ALL THE GRAPH AND TREES TO GENERATE NEW TREES


        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(280, 210, 261, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(13)
        self.label_6.setFont(font)
        self.label_6.setTextFormat(QtCore.Qt.AutoText)
        self.label_6.setScaledContents(False)
        self.label_6.setWordWrap(False)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(280, 450, 261, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(13)
        self.label_7.setFont(font)
        self.label_7.setTextFormat(QtCore.Qt.AutoText)
        self.label_7.setScaledContents(False)
        self.label_7.setWordWrap(False)
        self.label_7.setObjectName("label_7")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def click_arquivos(self):
        self.initialize()
    def onActivated(self,text):
        global grafo,selectedBox
        selectedBox=text
        grafo = self.gerargrafo(selectedBox)
    def primButton(self):
        global grafo
        global custo
        global arvore
        custo, arvore, grafo = self.prim()
        self.label_7.setText("O custo da AGMI é:"+str(custo))
        pos = nx.get_node_attributes(grafo, 'pos')
        nx.draw(arvore, pos, with_labels=True)
        plt.show()

    def kruskalButton(self):
        global grafo
        global custo
        global arvore
        custo, mst= self.kruskal()
        arvore,mst,custo= self.return_edges_Kruskal(mst)
        self.label_7.setText("O custo da AGMI é:"+str(custo))
        pos = nx.get_node_attributes(grafo, 'pos')
        nx.draw(arvore, pos, with_labels=True)
        plt.show()
    def heuristica(self):
        global grafo,selectedBox
        global arvore
        global custo
        arvore, custo = self.refinement_heuristic()
        self.label_7.setText("O custo da AGMI refinada é:"+str(custo))
        pos = nx.get_node_attributes(grafo, 'pos')
        nx.draw(arvore, pos, with_labels=True)
        plt.show()

    def resetGraph(self):
        global grafo,selectedBox
        grafo = self.gerargrafo(selectedBox)
        self.label_7.setText("Grafo resetado: "+selectedBox)

        
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("AGMI Algoritmos", "AGMI Algoritmos"))
        self.label.setText(_translate("MainWindow", "Árvore Geradora Mínima com Pesos nos Vértices Internos"))
        self.label_2.setText(_translate("MainWindow", "Selecione o arquivo:"))
        self.label_3.setText(_translate("MainWindow", "Frederico Resende e Luiz Felipe Chaves    |   Disciplina de grafos, Professora Dra. Fernanda Sumika Hojo de Souza"))
        self.label_6.setText(_translate("MainWindow", "Clique no algoritmo que deseja executar:"))
        
#        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
#"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
#"p, li { white-space: pre-wrap; }\n"
#"</style></head><body style=\" font-family:\'Uroob\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
#"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">custo</p></body></html>"))

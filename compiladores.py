class tabelaSimbolos():
	def __init__(self, linha, rotulo, token):
		self.linha = linha
		self.rotulo = rotulo
		self.token = token
	def __str__(self):
		return "Linha: " + "{:5}".format(str(self.linha)) + " Rotulo: " + "{:15}".format(self.rotulo) + " Token: " + "{:15}".format(self.token)

class erroLexicos():
	def __init__(self, linha, texto):
		self.linha = linha
		self.texto = texto
	def __str__(self):
		return "Erro na linha " + str(self.linha) + "\n\t" + str(self.texto)

def ler_tokens():
	l = []
	tokens = {}
	t = open('tokens.in').readlines()
	for i in t:
		l.append(i.replace("\n", ""))
	for i in l:
		temp = i.split(' ')
		tokens[temp[0]] = temp[1]
	return tokens

def ler_AFD(estadosFinais):
	t = open('AFD.in').readlines()
	lista = []
	for i in t:
		temp = []
		i = i.split(' ')
		if '::=' in i:
			i.remove('::=')
		while '|' in i:
			i.remove('|')
		if '\n' in i:
			i.remove('\n')
		temp.append(i[0])
		temp.append(i[1:])
		lista.append(temp)
	for i in lista:
		if 'eps' in i[1]:
			estadosFinais.append(i[0])
	return lista

def lerSimbolos():
	t = open('Gramatica/simbolos.in').readlines()
	s = []
	for i in t:
		i = i.split(' ')
		s.append(i[1].replace("\n", ""))
	return s

def lerEstados():
	t = open('Gramatica/estados.in')
	estados = []
	temp = []
	for i in t:
		i = i.replace("\n", "")
		i = i.split("State .*")
		if('' not in i):
			temp.append(i)
		else:
			estados.append(temp)
			temp = []
	estados.append(temp)
	return estados

def lerRegras():
	t = open('Gramatica/regras.in')
	s = []
	for i in t:
		i = i.split(' ')
		temp = []
		temp.append(i[1])
		aux = []
		for j in i[3:]:
			aux.append(j.replace("\n", ""))
		temp.append(aux)
		s.append(temp)
	return s

def getProxEstado(AFD, estado, letra):
	for i in AFD:
		if i[0] == estado:
			for j in i[1]:
				if j[0] == letra:
					return j[1:]
	return '<->'

def analizadorLexico(AFD, cFonte, estadosFinais, tokens):
	fita = []
	erros = []
	linha = 1
	flag = False
	temp = ''
	estado = '<S>'
	c = []
	for i in cFonte:
		c.append(i)
		identacao = True
		for j in i:
			# Para poder identar com \t
			if j == '\t' and identacao == True:
				continue
			# Se a flag de erro for falsa, percorre o codigo até achar um separador ou erro
			# senão busca um separador e adiciona a linha, o rotulo correspondentes e o token como erro na tabela
			if not flag:
				# Busca um separador, senão percorre o codigo e o AFD
				if j == ' ' or j == '\n':
					# Adiciona na tabela de símbolo o número da linha, o rotulo, se o estado atual está nos
					# estados finais, adiona o token correspondente,
					# senão adiciona o token de erro e adiciona o linha a lista de erros
					if estado in estadosFinais:
						fita.append(tabelaSimbolos(linha, temp, tokens[estado]))
					else:
						fita.append(tabelaSimbolos(linha, temp, 'erro'))
						erros.append(erroLexicos(linha, i))
					temp = ''
					estado = '<S>'
				else:
					identacao = False
					estado = getProxEstado(AFD, estado, j)
					temp += j
					# Se a transição para o próximo estado não existir muda a flag de erro para verdadeiro e adiciona
					# a linha aos erros
					if estado == '<->':
						erros.append(erroLexicos(linha, i))
						flag = True;
			else:
				if j == ' ' or j == '\n':
					fita.append(tabelaSimbolos(linha, temp, 'erro'))
					temp = ''
					estado = '<S>'
					flag = False
				else:
					temp += j
		linha += 1
	temp = []
	# Printa a tabela
	for i in fita:
		aux = []
		aux.append(i.token)
		aux.append(i.linha)
		temp.append(aux)
		print(i)
	# Printa os erros
	for i in erros:
		print(i)
	# Se não houver erros passa para o analisador sintático
	if len(erros) == 0:
		simbolos = lerSimbolos()
		estados = lerEstados()
		regras = lerRegras()
		parser = criarParser(simbolos, estados)
		analizadorSintatico(temp, regras, parser, c)

# Cria a tabela de parser
# Ex: [[{'WHILE': ['r', '1'], 'IF': ['s', '2']}] linha 0 -> 'WHILE' reducao da regra 1, 'IF' empilhamento 2
#      [{'ELSE': ['g', '1'], '$': [a]}]] linha 1 -> 'ELSE' salto para estado 1, '$' aceita
def criarParser(simbolos, estados):
	parser = []
	for i in estados:
		p = {}
		for j in i[1:]:
			j = j[0].split(' ')
			temp = []
			for x in j[1:]:
				temp.append(x)
			p[j[0]] = temp
		parser.append(p)
	return parser

def getTopoPilha(pilha):
	return pilha[len(pilha) - 1]

def getTopoFita(fita):
	if len(fita) >= 1:
		return fita[0]
	return False

def tamRegra(regra):
	if len(regra) == 1 and regra[0] == '':
		return 0
	return len(regra) * 2

def printSaida(pilha, fita, acao):
	print('\n------------------------------------------------------------------------------------------------')
	if len(pilha) > 10:
		pilha = pilha[len(pilha)-10:]
	print('Pilha: ', pilha)
	if len(fita) > 10:
		fita = fita[0:9]
	temp = []
	for i in fita:
		temp.append(i[0])
	print('Fita: ', temp)
	if acao[0] == 'a':
		print('[AC]')
	else:
		print('[' + acao[0] + acao[1] + ']')


def analizadorSintatico(fita, regras, parser, cFonte):
	pilha = []
	pilha.append(0)
	fita.append(["'$'", ''])
	fita.append(["(EOF)", ''])
	while(1):
		topP = getTopoPilha(pilha) # Pega o topo da pilha
		topF = getTopoFita(fita[0]) # Pega o topo da fila
		# Se o símbolo que da nome a regra está no índice da tabela então realiza as ações
		# senão erro encontrado
		if topF in parser[topP]:
			printSaida(pilha, fita, parser[topP][topF])
			if parser[topP][topF][0] == 's': # Empilhamento
				pilha.append(topF) # Adiciona o símbolo que da nome a regra na pilha
				pilha.append(int(parser[topP][topF][1])) # Adciona o número do próximo estado na pilha
				fita = fita[1:]	# Remove o primeiro elemento da fita
			elif parser[topP][topF][0] == 'r': # Redução
				tam = tamRegra(regras[int(parser[topP][topF][1])][1]) # Tamanho da regra * 2
				pilha = pilha[0:len(pilha)-tam] # Remove o tamanho da regra * 2 da pilha
				pilha.append(regras[int(parser[topP][topF][1])][0]) # Adiciona o símbolo que da nome a regra na pilha
				pilha.append(int(parser[pilha[len(pilha)-2]][pilha[len(pilha)-1]][1])) # Adiciona o próximo estado olhando o 
				# símbolo que da nome a regra e o estado antecessor ao símbolo que foi adicionado
			elif parser[topP][topF][0] == 'a': # Aceita o codigo fonte
				break
		else:
			printSaida(pilha, fita, ['ERRO', ''])
			print('Erro na linha ' + str(fita[0][1]) + ':\n\t' + cFonte[fita[0][1] - 1])
			break

estadosFinais = []
afd = ler_AFD(estadosFinais)
tokens = ler_tokens()
codigoFonte = open('codigo.in')
analizadorLexico(afd, codigoFonte, estadosFinais, tokens)

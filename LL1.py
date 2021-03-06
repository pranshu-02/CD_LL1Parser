import re
import string
#Parser Class
class LL1Parser:
	start_sym=""
	productions={}
	first_table= {}
	follow_table= {}
	table={}
	def __init__(self,file='grammar3'):
		grammar = open(file, "r")
		self.Create_Productions(grammar)
		for nt in self.productions:
			self.first_table[nt] = self.Cal_first(nt)
		self.follow_table[self.start_sym] = set('$')
		for nt in self.productions:
			self.follow_table[nt] = self.Cal_follow(nt)
		self.Create_Table()

#Check if sym is Non-Terminal		
	def isNonterminal(self,sym):
		if sym.isupper():
			return True
		else:
			return False
#Create Productions Dict From Given Grammar
	def Create_Productions(self,grammar):
		for production in grammar:
			lhs,rhs=re.split("->",production)
			rhs = re.split("\||\n",rhs)
			self.productions[lhs]=set(rhs)-{''}
			if not self.start_sym:
				self.start_sym = lhs
#Calculate First Set Of Given Symbol 
	def Cal_first(self,sym):
		if sym in self.first_table:
			return self.first_table[sym];
		if self.isNonterminal(sym):
			first = set()
			for x in self.productions[sym]:
				if x == '@':				
					first = first.union('@')
				else:
					for i in x:	
						fst = self.Cal_first(i)
						if i != x[-1]:
							first = first.union(fst-{'@'})
						else:
							first = first.union(fst)
						if '@' not in fst:
							break
			return first;
		else:
			return set(sym)
#Calculate Follow Set Of Given Symbol 
	def Cal_follow(self, sym):
		if sym not in self.follow_table:
			self.follow_table[sym] = set() 
		for nt in self.productions.keys():
			for rule in self.productions[nt]:
				pos = rule.find(sym)
				if pos!=-1:
					if pos == (len(rule)-1):
						if nt != sym:
							self.follow_table[sym] = self.follow_table[sym].union(self.Cal_follow(nt))
					else:
						first_next = set()
						for next in rule[pos+1:]:
							fst_next = self.Cal_first(next)
							first_next = first_next.union(fst_next-{'@'})
							if '@' not in fst_next:
								break
						if '@' in fst_next:
							if nt != sym:
								self.follow_table[sym] = self.follow_table[sym].union(self.Cal_follow(nt))
								self.follow_table[sym] = self.follow_table[sym].union(first_next) - {'@'}
						else:
							self.follow_table[sym] = self.follow_table[sym].union(first_next)
		return self.follow_table[sym]
#Create Parsing Table
	def Create_Table(self):
		for nt in self.productions:
			for rule in self.productions[nt]:
				first_rule = set()
				for sym in rule:
					fst_sym = self.Cal_first(sym)
					first_rule = first_rule.union(fst_sym-{'@'})
					if '@' not in fst_sym:
						break
				if '@' in fst_sym:
					first_rule.add('@')
				for element in first_rule:
					self.table[nt,element] = rule
				if '@' in first_rule:
					for element in self.follow_table[nt]:
						self.table[nt,element] = rule
#Print First,Follow Sets and Parsing Table
	def PrintDetails(self):
		import pandas as pd
		print("!! First Sets !!")
		for nt in self.productions:
			print(nt+":"+str(self.first_table[nt]))
		print("\n")
		print("!! Follow Sets !!")
		for nt in self.productions:
			print(nt+":"+str(self.follow_table[nt]))
		print("\n")
		print("!! Parsing Table !!")
		temp_table={}
		for key in self.table:
			temp_table[key[1]]={}
		for key in self.table:
			temp_table[key[1]][key[0]] = (key[0]+"->"+self.table[key])
		print(pd.DataFrame(temp_table).fillna('Error'))
		print("\n")
#Parse A Given String According to grammar
	def Parse(self,input):
		input=input+"$"
		stack = []
		f = 0		
		stack.append("$")
		stack.append(self.start_sym)
		input_length = len(input)
		cur_index = 0
		print(f"{'Stack' : <20}{'Input' : ^20}{'Action' : >20}")
		while len(stack) > 0:
			TOS = stack[len(stack)-1]
			current_input = input[cur_index]
			if TOS == current_input and TOS == '$':
				f=1
				break	
			elif TOS == current_input:
				print(f"{(''.join(stack)) : <20}{input[cur_index:] : ^20}{'Match' : >20}")
				stack.pop()
				cur_index+=1
			else:	
				key = TOS,current_input
				if key not in self.table:
					f=0		
					break
				rule=self.table[key]
				action = str(TOS)+"->"+str(rule)
				print(f"{(''.join(stack)) : <20}{input[cur_index:] : ^20}{action : >20}")
				if rule !='@':
					rule = rule[::-1]
					stack.pop()
					for sym in list(rule):
						stack.append(sym)
				else:
					stack.pop()		

		if f == 0:
			print("String Not Accepted!!")
		else:
			print("String Accepted!")

##Main Function 
if __name__ == "__main__":
	parser = LL1Parser()
	parser.PrintDetails()
	parser.Parse("acdg")
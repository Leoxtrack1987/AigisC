from Objetos.Nodo import Nodo
from Sintactico.TablaSintactico import TablaSimbolos

class Sintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla = TablaSimbolos()
        self.errores = []
        self.ast = None
        self.primarios = {"void","int","float","char","bool","string"}
        self.modificadores = {"const","readonly","global","local","shared"}

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def avanzar(self):
        self.pos += 1

    def comparar(self, tipo=None, valor=None):
        token = self.actual()
        if token and ((tipo is None or token.tipo == tipo) and (valor is None or token.valor == valor)):
            self.avanzar()
            return token
        else:
            esperado = valor if valor else tipo
            encontrado = token.valor if token else "EOF"
            self.error(f"Se esperaba '{esperado}' pero se encontró '{encontrado}'.")
            return None

    def error(self, mensaje):
        token = self.actual()
        linea = token.linea if token else "?"
        columna = token.columna if token else "?"
        self.errores.append(f"Error sintáctico en línea {linea}, columna {columna}: {mensaje}")

    def analisis_sintactico(self):
        cuerpo = []
        while self.actual():
            pos_inicial = self.pos
            nodo = self.instruccion()
            if nodo:
                cuerpo.append(nodo)
            if self.pos == pos_inicial:
                self.avanzar()
        self.ast = Nodo("Programa", hijos=cuerpo)
        return self.ast

    def instruccion(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "Reservada":
            if token.valor == "if":
                return self.instruccion_if()
            if token.valor == "while":
                return self.instruccion_while()
            if token.valor == "for":
                return self.instruccion_for()
            if token.valor == "try":
                return self.instruccion_try()
            if token.valor == "throw":
                return self.instruccion_throw()
            if token.valor == "function":
                return self.declaracion_funcion()
            if token.valor == "model":
                return self.declaracion_modelo()
            if token.valor == "template":
                return self.declaracion_template()
            if token.valor in ("import","from"):
                return self.importacion()
            if token.valor in self.modificadores or token.valor in self.primarios or token.valor in ("mapInt","mapString"):
                return self.declaracion_variable()
            if token.valor == "return":
                return self.instruccion_return()

        if token.tipo.startswith("Comentario"):
            self.avanzar()
            return None
        if token.tipo == "Identificador":
            return self.asignacion()
        self.error(f"Instrucción inesperada: '{token.valor}'")
        self.avanzar()
        return None

    def instruccion_if(self):
        self.comparar("Reservada","if")
        self.comparar("ParentIzq")
        cond = self.condicion()
        self.comparar("ParentDer")
        self.comparar("LlaveIzq")
        cuerpo = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            nodo = self.instruccion()
            if nodo: cuerpo.append(nodo)
        self.comparar("LlaveDer")
        fallback = None
        if self.actual() and self.actual().tipo == "Reservada" and self.actual().valor == "else":
            self.avanzar()
            if self.actual() and self.actual().tipo == "LlaveIzq":
                self.comparar("LlaveIzq")
                else_cuerpo = []
                while self.actual() and self.actual().tipo != "LlaveDer":
                    n = self.instruccion()
                    if n: else_cuerpo.append(n)
                self.comparar("LlaveDer")
                fallback = Nodo("Else", hijos=else_cuerpo)
            elif self.actual() and self.actual().tipo == "Reservada" and self.actual().valor == "if":
                fallback = self.instruccion_if()
        return Nodo("If", hijos=[cond, Nodo("Bloque", hijos=cuerpo)] + ([fallback] if fallback else []))

    def instruccion_while(self):
        self.comparar("Reservada","while")
        self.comparar("ParentIzq")
        cond = self.condicion()
        self.comparar("ParentDer")
        self.comparar("LlaveIzq")
        cuerpo = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            nodo = self.instruccion()
            if nodo: cuerpo.append(nodo)
        self.comparar("LlaveDer")
        return Nodo("While", hijos=[cond, Nodo("Bloque", hijos=cuerpo)])

    def instruccion_for(self):
        self.comparar("Reservada", "for")
        self.comparar("ParentIzq")
        
        # Determinar si es for de rango o iterable
        # For rango: (variable ; condicion ; variable incrementador)
        # For iterable: tipo variable in lista
        
        # Guardar posición para backtrack si es necesario
        pos_checkpoint = self.pos
        
        # Intentar parsear como for de rango
        es_rango = False
        if self.actual() and self.actual().tipo == "Identificador":
            # Mirar adelante para ver si hay punto y coma
            temp_pos = self.pos + 1
            if temp_pos < len(self.tokens) and self.tokens[temp_pos].tipo == "PuntoComa":
                es_rango = True
        
        if es_rango:
            # For rango: (variable ; condicion ; variable incrementador)
            var1 = self.comparar("Identificador")
            self.comparar("PuntoComa")
            cond = self.condicion()
            self.comparar("PuntoComa")
            var2 = self.comparar("Identificador")
            incr = self.comparar("Incrementador")  # CORREGIDO: era "Incrementador"
            self.comparar("ParentDer")
            self.comparar("LlaveIzq")
            cuerpo = []
            while self.actual() and self.actual().tipo != "LlaveDer":
                n = self.instruccion()
                if n: cuerpo.append(n)
            self.comparar("LlaveDer")
            return Nodo("ForRango", valor=(var1.valor if var1 else None), hijos=[
                Nodo("Variable", valor=(var1.valor if var1 else None)),
                cond,
                Nodo("Variable", valor=(var2.valor if var2 else None)),
                Nodo("Incrementador", valor=(incr.valor if incr else None)),
                Nodo("Bloque", hijos=cuerpo)
            ])
        else:
            # For iterable: tipo variable in lista
            tipo = self.tipo_dato()
            var = self.comparar("Identificador")
            self.comparar("Reservada", "in")
            lista = self.expresion()
            self.comparar("ParentDer")
            self.comparar("LlaveIzq")
            cuerpo = []
            while self.actual() and self.actual().tipo != "LlaveDer":
                n = self.instruccion()
                if n: cuerpo.append(n)
            self.comparar("LlaveDer")
            return Nodo("ForIter", hijos=[
                Nodo("Tipo", valor=tipo),
                Nodo("Variable", valor=(var.valor if var else None)),
                lista,
                Nodo("Bloque", hijos=cuerpo)
            ])

    def instruccion_try(self):
        self.comparar("Reservada","try")
        self.comparar("LlaveIzq")
        cuerpo = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            n = self.instruccion()
            if n: cuerpo.append(n)
        self.comparar("LlaveDer")
        self.comparar("Reservada","catch")
        self.comparar("ParentIzq")
        self.comparar("Reservada","error")
        errname = self.comparar("Identificador")
        self.comparar("ParentDer")
        self.comparar("LlaveIzq")
        cuerpo2 = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            n = self.instruccion()
            if n: cuerpo2.append(n)
        self.comparar("LlaveDer")
        return Nodo("TryCatch", hijos=[
            Nodo("Bloque", hijos=cuerpo),
            Nodo("Catch", valor=(errname.valor if errname else None), hijos=cuerpo2)
        ])

    def instruccion_throw(self):
        self.comparar("Reservada","throw")
        ident = self.comparar("Identificador")
        if self.actual() and self.actual().tipo == "PuntoComa":
            self.avanzar()
        return Nodo("Throw", valor=(ident.valor if ident else None))

    def declaracion_funcion(self, es_miembro=False, con_override=False):
        """
        Parsea declaraciones de función
        es_miembro: si es parte de un modelo
        con_override: si tiene modificador override
        """
        # Puede tener tipo de retorno explícito o "function"
        tipo_retorno = None
        if self.actual() and self.actual().tipo == "Reservada":
            if self.actual().valor in self.primarios:
                tipo_retorno = self.comparar("Reservada").valor
            elif self.actual().valor == "function":
                self.comparar("Reservada","function")
                tipo_retorno = "void"
        
        nombre = self.comparar("Identificador")
        self.comparar("ParentIzq")
        params = self.parse_params()
        self.comparar("ParentDer")
        self.comparar("LlaveIzq")
        cuerpo = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            n = self.instruccion()
            if n: cuerpo.append(n)
        self.comparar("LlaveDer")
        
        if nombre and not es_miembro:
            simbolo = {
                "identificador": nombre.valor,
                "categoria": "función",
                "tipo_dato": tipo_retorno or "void",
                "ambito": "global",
                "direccion_memoria": None,
                "linea": nombre.linea,
                "valor": None,
                "estado": "declarado",
                "estructura": None,
                "referencias": 0
            }
            self.tabla.agregar(simbolo)
        
        nodo_tipo = Nodo("TipoRetorno", valor=tipo_retorno or "void")
        nodo_params = Nodo("Params", hijos=params)
        
        if con_override:
            return Nodo("FuncionOverride", valor=(nombre.valor if nombre else None), 
                       hijos=[nodo_tipo, nodo_params] + cuerpo)
        else:
            return Nodo("FuncionDeclarada", valor=(nombre.valor if nombre else None), 
                       hijos=[nodo_tipo, nodo_params] + cuerpo)

    def parse_params(self):
        params = []
        while self.actual() and self.actual().tipo != "ParentDer":
            tipo = self.tipo_dato()
            nombre = self.comparar("Identificador")
            params.append(Nodo("Param", valor=(nombre.valor if nombre else None), 
                             hijos=[Nodo("Tipo", valor=tipo)]))
            if self.actual() and self.actual().tipo == "Coma":
                self.avanzar()
            else:
                break
        return params

    def tipo_dato(self):
        """
        Parsea tipo_dato según gramática:
        tipo_dato ::= primitivo | lista | modelo | funcion
        lista ::= tipo_dato '[]' | 'mapInt' tipo_dato '{}' | 'mapString' tipo_dato '{}'
        """
        tipo_base = None
        
        if self.actual() and self.actual().tipo == "Reservada":
            if self.actual().valor in self.primarios:
                tipo_base = self.comparar("Reservada").valor
            elif self.actual().valor in ("mapInt", "mapString"):
                map_type = self.comparar("Reservada").valor
                # En mapInt/mapString puede venir tipo seguido de {}
                if self.actual() and (self.actual().tipo == "Reservada" or self.actual().tipo == "Identificador"):
                    inner_type = self.tipo_dato()
                    tipo_base = f"{map_type}<{inner_type}>"
                else:
                    tipo_base = map_type
        elif self.actual() and self.actual().tipo == "Identificador":
            tipo_base = self.comparar("Identificador").valor
        else:
            self.error("Tipo de dato esperado")
            return None
        
        # Verificar si es un array []
        if self.actual() and self.actual().tipo == "CorcheteIzq":
            self.comparar("CorcheteIzq")
            self.comparar("CorcheteDer")
            return f"{tipo_base}[]"
        
        # Verificar si es un mapa {}
        if self.actual() and self.actual().tipo == "LlaveIzq":
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            # Solo consumir {} si no es inicio de bloque
            if next_token and next_token.tipo == "LlaveDer":
                self.comparar("LlaveIzq")
                self.comparar("LlaveDer")
                return f"{tipo_base}{{}}"
        
        return tipo_base

    def declaracion_modelo(self):
        self.comparar("Reservada","model")
        nombre = self.comparar("Identificador")

        # Manejo de herencia
        parent = None
        if self.actual() and self.actual().tipo == "Reservada" and self.actual().valor == "extends":
            self.comparar("Reservada","extends")
            parent = self.comparar("Identificador")

        self.comparar("LlaveIzq")
        miembros = []

        while self.actual() and self.actual().tipo != "LlaveDer":
            token = self.actual()
            
            # Verificar si es override
            es_override = False
            if token.tipo == "Reservada" and token.valor == "override":
                self.comparar("Reservada", "override")
                es_override = True
                token = self.actual()
            
            if token.tipo == "Reservada":
                # Función miembro con tipo explícito o function
                if token.valor in self.primarios:
                    # Mirar si es función
                    next_token = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
                    next_next = self.tokens[self.pos+2] if self.pos+2 < len(self.tokens) else None
                    if next_token and next_token.tipo == "Identificador" and next_next and next_next.tipo == "ParentIzq":
                        miembros.append(self.declaracion_funcion(es_miembro=True, con_override=es_override))
                    else:
                        miembros.append(self.declaracion_variable())
                elif token.valor == "function":
                    miembros.append(self.declaracion_funcion(es_miembro=True, con_override=es_override))
                elif token.valor in self.modificadores:
                    miembros.append(self.declaracion_variable())
                else:
                    self.error(f"Miembro inesperado en modelo: '{token.valor}'")
                    self.avanzar()
            elif token.tipo == "Identificador":
                # Variables con tipo definido como Identificador
                miembros.append(self.declaracion_variable())
            else:
                self.error(f"Miembro inesperado en modelo: '{token.valor}'")
                self.avanzar()

        self.comparar("LlaveDer")

        ast_hijos = []
        if parent:
            ast_hijos.append(Nodo("Extends", valor=(parent.valor if parent else None)))
        ast_hijos += miembros

        # Agregar símbolo del modelo a la tabla
        if nombre:
            simbolo = {
                "identificador": nombre.valor,
                "categoria": "modelo",
                "tipo_dato": None,
                "ambito": "global",
                "direccion_memoria": None,
                "linea": nombre.linea,
                "valor": None,
                "estado": "declarado",
                "estructura": miembros,
                "referencias": 0
            }
            self.tabla.agregar(simbolo)

        return Nodo("Modelo", valor=(nombre.valor if nombre else None), hijos=ast_hijos)

    def declaracion_template(self):
        """Parsea template (interfaz)"""
        self.comparar("Reservada", "template")
        nombre = self.comparar("Identificador")
        self.comparar("LlaveIzq")
        
        firmas = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            # Las templates solo tienen firmas de funciones
            tipo = self.tipo_dato()
            nombre_func = self.comparar("Identificador")
            self.comparar("ParentIzq")
            params = self.parse_params()
            self.comparar("ParentDer")
            self.comparar("PuntoComa")
            
            firmas.append(Nodo("FirmaFuncion", valor=(nombre_func.valor if nombre_func else None),
                             hijos=[Nodo("Tipo", valor=tipo), Nodo("Params", hijos=params)]))
        
        self.comparar("LlaveDer")
        
        if nombre:
            simbolo = {
                "identificador": nombre.valor,
                "categoria": "template",
                "tipo_dato": None,
                "ambito": "global",
                "direccion_memoria": None,
                "linea": nombre.linea,
                "valor": None,
                "estado": "declarado",
                "estructura": firmas,
                "referencias": 0
            }
            self.tabla.agregar(simbolo)
        
        return Nodo("Template", valor=(nombre.valor if nombre else None), hijos=firmas)

    def importacion(self):
        if self.actual() and self.actual().valor == "import":
            self.comparar("Reservada","import")
            mod = self.comparar("Identificador")
            if self.actual() and self.actual().tipo == "PuntoComa":
                self.avanzar()
            return Nodo("Import", valor=(mod.valor if mod else None))
        else:
            self.comparar("Reservada","from")
            mod = self.comparar("Identificador")
            self.comparar("Reservada","import")
            deps = []
            while True:
                d = self.comparar("Identificador")
                if d: deps.append(d.valor)
                if self.actual() and self.actual().tipo == "Coma":
                    self.avanzar()
                    continue
                break
            if self.actual() and self.actual().tipo == "PuntoComa":
                self.avanzar()
            return Nodo("FromImport", valor=mod.valor if mod else None, 
                       hijos=[Nodo("Deps", hijos=[Nodo("Dep", valor=x) for x in deps])])

    def declaracion_variable(self, in_paren=False):
        modifiers = []
        while self.actual() and self.actual().tipo == "Reservada" and self.actual().valor in self.modificadores:
            modifiers.append(self.comparar("Reservada").valor)

        # Tipo de dato
        tipo_token = self.tipo_dato()
        
        if not tipo_token:
            self.error("Tipo de dato esperado")
            return None

        name = self.comparar("Identificador")

        valor_node = None
        if self.actual() and self.actual().tipo == "Asignacion":
            self.comparar("Asignacion")
            # Verificar si es inicialización de lista/mapa
            if self.actual() and self.actual().tipo == "LlaveIzq":
                valor_node = self.valor_lista()
            else:
                valor_node = self.expresion()

        # Manejo de ';' dentro y fuera de paréntesis
        if self.actual() and self.actual().tipo == "PuntoComa":
            self.avanzar()
        elif not in_paren:
            pass  # Relajar el requisito del punto y coma en algunos contextos

        # Agregar a tabla de símbolos
        simbolo = {
            "identificador": name.valor if name else None,
            "categoria": "variable",
            "tipo_dato": tipo_token,
            "ambito": ("global" if "global" in modifiers else "local"),
            "direccion_memoria": None,
            "linea": (name.linea if name else None),
            "valor": None,
            "estado": "declarado",
            "estructura": None,
            "referencias": 0
        }
        self.tabla.agregar(simbolo)

        hijos = [Nodo("Tipo", valor=tipo_token)]
        if modifiers:
            hijos.insert(0, Nodo("Modificadores", valor=",".join(modifiers)))
        if valor_node:
            hijos.append(valor_node)
        
        return Nodo("DeclaracionVariable", valor=(name.valor if name else None), hijos=hijos)

    def valor_lista(self):
        """
        Parsea valores de listas/mapas con sintaxis key:value o solo valores
        valor_lista ::= ( numero ':' valor | texto ':' valor ) ( ',' valor_lista )?
        """
        self.comparar("LlaveIzq")
        vals = []
        
        while self.actual() and self.actual().tipo != "LlaveDer":
            # Puede ser key:value o solo value
            first = self.expresion()
            
            if self.actual() and self.actual().tipo == "DosPuntos":
                self.comparar("DosPuntos")
                second = self.expresion()
                vals.append(Nodo("ParClaveValor", hijos=[first, second]))
            else:
                vals.append(first)
            
            if self.actual() and self.actual().tipo == "Coma":
                self.avanzar()
            else:
                break
        
        self.comparar("LlaveDer")
        return Nodo("Lista", hijos=vals)

    def asignacion(self):
        ident = self.comparar("Identificador")
        
        if self.actual() and self.actual().tipo in ("Asignacion","AsignacionCompuesta"):
            operador = self.actual()
            self.avanzar()
        else:
            self.error("Se esperaba operador de asignación ('=', '+=', '-=', '*=', '/=')")
            return None
        
        expr = self.expresion()
        
        if self.actual() and self.actual().tipo == "PuntoComa":
            self.avanzar()
        
        simbolo = {
            "identificador": ident.valor if ident else None,
            "categoria": "variable",
            "tipo_dato": None,
            "ambito": "global",
            "direccion_memoria": None,
            "linea": (ident.linea if ident else None),
            "valor": None,
            "estado": "asignado",
            "estructura": None,
            "referencias": 0
        }
        self.tabla.agregar(simbolo)
        
        return Nodo("Asignacion", valor=(f"{ident.valor} {operador.valor}" if ident and operador else None), 
                   hijos=[expr])

    def expresion(self):
        return self.expresion_logica()

    def expresion_logica(self):
        izquierda = self.expresion_igualdad()
        while self.actual() and ((self.actual().tipo == "Logico") or 
                                (self.actual().tipo == "Reservada" and self.actual().valor in ("and","or","AND","OR"))):
            op = self.actual().valor
            self.avanzar()
            derecha = self.expresion_igualdad()
            izquierda = Nodo("OperacionLogica", valor=op, hijos=[izquierda, derecha])
        return izquierda

    def expresion_igualdad(self):
        izquierda = self.expresion_relacional()
        while self.actual() and (self.actual().tipo == "Relacional" and 
                                self.actual().valor in ("==","!=") or 
                                (self.actual().tipo == "Reservada" and self.actual().valor in ("is","is not"))):
            op = self.actual().valor
            self.avanzar()
            derecha = self.expresion_relacional()
            izquierda = Nodo("OperacionRelacional", valor=op, hijos=[izquierda, derecha])
        return izquierda

    def expresion_relacional(self):
        izquierda = self.expresion_aritmetica()
        while self.actual() and self.actual().tipo == "Relacional" and self.actual().valor in (">","<",">=","<="):
            op = self.actual().valor
            self.avanzar()
            derecha = self.expresion_aritmetica()
            izquierda = Nodo("OperacionRelacional", valor=op, hijos=[izquierda, derecha])
        return izquierda

    def expresion_aritmetica(self):
        nodo = self.termino()
        while self.actual() and self.actual().tipo == "Aritmetico" and self.actual().valor in ("+","-"):
            op = self.actual().valor
            self.avanzar()
            right = self.termino()
            nodo = Nodo("Operacion", valor=op, hijos=[nodo, right])
        return nodo

    def termino(self):
        nodo = self.factor()
        while self.actual() and self.actual().tipo == "Aritmetico" and self.actual().valor in ("*","/","%"):
            op = self.actual().valor
            self.avanzar()
            right = self.factor()
            nodo = Nodo("Operacion", valor=op, hijos=[nodo, right])
        return nodo

    def factor(self):
        token = self.actual()
        if not token:
            return Nodo("ErrorExpresion", valor="EOF")

        # Números
        if token.tipo == "Numero":
            self.avanzar()
            return Nodo("Numero", valor=token.valor)
        
        # Cadenas
        if token.tipo == "Cadena":
            self.avanzar()
            return Nodo("Cadena", valor=token.valor)
        
        # Booleanos
        if token.tipo == "Reservada" and token.valor in ("true","false","1","0"):
            self.avanzar()
            return Nodo("Booleano", valor=token.valor)

        # Identificadores y llamadas a función
        if token.tipo == "Identificador":
            self.avanzar()
            
            # Llamada a función
            if self.actual() and self.actual().tipo == "ParentIzq":
                self.comparar("ParentIzq")
                args = []
                while self.actual() and self.actual().tipo != "ParentDer":
                    args.append(self.expresion())
                    if self.actual() and self.actual().tipo == "Coma":
                        self.avanzar()
                self.comparar("ParentDer")
                return Nodo("LlamadaFuncion", valor=token.valor, hijos=args)
            
            # Acceso a array/map con []
            if self.actual() and self.actual().tipo == "CorcheteIzq":
                self.comparar("CorcheteIzq")
                indice = self.expresion()
                self.comparar("CorcheteDer")
                return Nodo("AccesoIndice", valor=token.valor, hijos=[indice])
            
            # Incremento/decremento postfijo
            if self.actual() and self.actual().tipo == "Incrementador":
                op = self.comparar("Incrementador")
                return Nodo("IncrementoPostfijo", valor=f"{token.valor}{op.valor}")
            
            return Nodo("Identificador", valor=token.valor)

        # Expresiones entre paréntesis
        if token.tipo == "ParentIzq":
            self.comparar("ParentIzq")
            n = self.expresion()
            self.comparar("ParentDer")
            return n

        # Listas/mapas literales con llaves
        if token.tipo == "LlaveIzq":
            return self.valor_lista()

        # Funciones anónimas
        if token.tipo == "Reservada" and token.valor == "function":
            return self.funcion_anonima()
        
        # Operador NOT unario
        if token.tipo == "Logico" and token.valor == "!":
            self.avanzar()
            operando = self.factor()
            return Nodo("OperacionLogica", valor="!", hijos=[operando])
        
        if token.tipo == "Reservada" and token.valor in ("not", "NOT"):
            self.avanzar()
            operando = self.factor()
            return Nodo("OperacionLogica", valor="not", hijos=[operando])
        
        # Operadores unarios + y -
        if token.tipo == "Aritmetico" and token.valor in ("+", "-"):
            op = token.valor
            self.avanzar()
            operando = self.factor()
            return Nodo("OperacionUnaria", valor=op, hijos=[operando])

        self.error(f"Expresión no válida cerca de '{token.valor}'")
        self.avanzar()
        return Nodo("ErrorExpresion", valor=token.valor)

    def condicion(self):
        """
        Parsea condición según gramática:
        condicion ::= condicion_unitaria | 'bool' | condicion logicos condicion
        """
        return self.expresion()

    def funcion_anonima(self):
        """Parsea funciones anónimas"""
        self.comparar("Reservada","function")
        self.comparar("ParentIzq")
        params = self.parse_params()
        self.comparar("ParentDer")
        self.comparar("LlaveIzq")
        cuerpo = []
        while self.actual() and self.actual().tipo != "LlaveDer":
            n = self.instruccion()
            if n: cuerpo.append(n)
        self.comparar("LlaveDer")
        return Nodo("FuncionAnonima", hijos=[Nodo("Params", hijos=params)] + cuerpo)
    
    def instruccion_return(self):
        """Parsea instrucción return"""
        self.comparar("Reservada","return")
        expr = None
        if self.actual() and self.actual().tipo != "PuntoComa":
            expr = self.expresion()
        if self.actual() and self.actual().tipo == "PuntoComa":
            self.comparar("PuntoComa")
        return Nodo("Return", hijos=[expr] if expr else [])
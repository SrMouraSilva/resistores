import pygraphviz
from IPython.display import Image
from IPython.display import SVG


class DP:
    """
    Singleton for generate unique id for Dot Point in circuit
    """
    current = 0
    
    @staticmethod
    def generate():
        DP.current += 1
        
        return 'dp_{}'.format(DP.current)


class DictList():
    
    def __init__(self):
        self.dict = {}
    
    def __getitem__(self, index):
        if index not in self.dict:
            self.dict[index] = []
        
        return self.dict[index]


class GeapGraphGenerator(object):
    
    def __init__(self, nodes, edges, labels):
        self.nodes, self.edges, self.labels = nodes, edges, labels
        self.adjacency = self.adjacency_list(self.edges)
        
    @staticmethod
    def by_expression(expression):
        from deap import gp
        return GeapGraphGenerator(*gp.graph(expression))

    def adjacency_list(self, edges):
        lista = DictList()
        
        for by, to in edges:
            lista[by].append(to)

        return lista.dict

    def generate(self):
        adpted_edges = self.adapt_edges(self.nodes[0], DP.generate())[0]
        
        return Graph(self.nodes, adpted_edges, self.labels)
        
    def adapt_edges(self, element, last_element):
        if self.labels[element] == 'paralelo':
            a, b = self.adjacency[element]
            return self.adapt_paralel(a, b, last_element)

        elif self.labels[element] == 'serie':
            a, b = self.adjacency[element]
            return self.adapt_series(a, b, last_element)

        else:
            return [(last_element, element)], element

    def adapt_paralel(self, circuit_a, circuit_b, last_element):
        head = DP.generate()

        a, a_tail = self.adapt_edges(circuit_a, head)
        b, b_tail = self.adapt_edges(circuit_b, head)

        tail = DP.generate()

        lista = [(last_element, head)] \
              + a \
              + b \
              + [(a_tail, tail), (b_tail, tail)]

        return lista, tail

    def adapt_series(self, circuit_a, circuit_b, last_element):
        list_first, first = self.adapt_edges(circuit_a, last_element)
        list_second, second = self.adapt_edges(circuit_b, first)

        return list_first + list_second, second


class Graph(object):
        
    def __init__(self, nodes, edges, labels):
        self.graph = pygraphviz.AGraph()
        self.graph.graph_attr['rankdir'] = 'LR'
        self.graph.add_edges_from(edges)
        self.graph.layout()
        
        get_node = lambda index: self.graph.get_node(str(index))
        
        self.edges = edges
        self.labels = labels
        self._nodes = [self._generate_node(get_node(node)) for node in self.graph.nodes()]
        

    def _generate_node(self, element):
        is_dp = str(element).startswith('dp_')
        
        return CircuitPoint(self, element) if is_dp else Resistor(self, element)

    @property
    def nodes(self):
        return self._nodes
    
    def draw(self):
        return SVG(self.graph.draw(format='svg', prog='dot'))

    def save(self, path, root):
        return self.graph.draw(format='svg', prog='dot', path=path)


class Element(object):
    
    def __init__(self, graph, element):
        self.graph = graph
        self.element = element
        
        self.style()
    
    def style(self):
        pass

class CircuitPoint(Element):
    
    def style(self):
        self.element.attr['shape'] = 'point'
        self.element.attr['width'] = 0.05


class Resistor(Element):
    
    def style(self):
        self.element.attr['label'] = ''
        #self.element.attr['label'] = labels[int(node_name)]
        self.element.attr['xlabel'] = '{} Ω'.format(self.graph.labels[int(self.element)])
        self.element.attr['shape'] = 'none'
        self.element.attr['image'] = 'img/resistor-original.svg'



import unittest

import owlready
from owlready import *

onto_path.append(os.path.dirname(__file__))


NB_ONTO = 0
def new_onto():
  global NB_ONTO
  NB_ONTO += 1
  return Ontology("http://test.org/onto_%s.owl" % NB_ONTO)

class Test(unittest.TestCase):
  def setUp(self): pass

  def test_reasonning_1(self):
    onto = new_onto()
    
    class Pizza     (Thing): ontology = onto
    class Ingredient(Thing): ontology = onto

    class a_pour_ingredient(InverseFunctionalProperty):
      ontology = onto
      domain   = [Pizza]
      range    = [Ingredient]
      
    class Legume   (Ingredient): pass
    class Tomate   (Legume):     pass
    class Aubergine(Legume):     pass
    class Fromage  (Ingredient): pass
    class Viande   (Ingredient): pass
    class Poisson  (Ingredient): pass
    class Thon     (Poisson):    pass
    
    onto.all_disjoints.append(AllDisjoint(Pizza, Ingredient))
    onto.all_disjoints.append(AllDisjoint(Legume, Fromage, Viande, Poisson))
    onto.all_disjoints.append(AllDisjoint(Tomate, Aubergine))
    
    class PizzaVegetarienne(Pizza):
      is_a = [
        NOT(restriction("a_pour_ingredient", SOME, Viande)) & NOT(restriction("a_pour_ingredient", SOME, Poisson)),
        ]

    class PizzaNonVegetarienne(Pizza):
      equivalent_to = [
        (Pizza & NOT(PizzaVegetarienne)),
        ]
      
    class PizzaAuThon(Pizza):
      is_a = [
        restriction("a_pour_ingredient", SOME, Tomate),
        restriction("a_pour_ingredient", SOME, Fromage),
        restriction("a_pour_ingredient", SOME, Thon),
        restriction("a_pour_ingredient", ONLY, Tomate | Fromage | Thon),
        ]
      
    ma_pizza = Pizza("ma_pizza",
      ontology = onto,
      a_pour_ingredient = [
        Tomate("tomate1"),
        Fromage("fromage1"),
        Thon("thon1"),
        ],
      a_pour_prix = 10.0
      )
    
    onto.sync_reasoner()
    assert issubclass(PizzaAuThon, PizzaNonVegetarienne)
    assert isinstance(ma_pizza   , PizzaNonVegetarienne)


  def test_inverse_prop_1(self):
    onto = new_onto()
    class Obj(Thing):
      ontology = onto
    class prop(Property):
      ontology = onto
      domain   = [Obj]
      range    = [Obj]
    class antiprop(Property):
      ontology = onto
      inverse_property = prop
      
    o1 = Obj()
    o2 = Obj()
    o1.prop.append(o2)
    assert o2 in o1.prop
    assert o1 in o2.antiprop
    
  def test_inverse_prop_2(self):
    onto = new_onto()
    class Obj(Thing):
      ontology = onto
    class prop(FunctionalProperty):
      ontology = onto
      domain   = [Obj]
      range    = [Obj]
    class antiprop(FunctionalProperty):
      ontology = onto
      inverse_property = prop
      
    o1 = Obj()
    o2 = Obj()
    o1.prop = o2
    assert o1.prop == o2
    assert o2.antiprop == o1
    

  def test_annotation1(self):
    onto = new_onto()
    class Obj(Thing): ontology = onto
    
    ANNOTATIONS[Obj][rdfs.comment] = "Test"
    assert(ANNOTATIONS[Obj]["comment"] == ["Test"])
    
  def test_annotation2(self):
    onto = new_onto()
    class Obj(Thing): ontology = onto
    
    ANNOTATIONS[Obj][rdfs.comment, "fr"] = "Med"
    ANNOTATIONS[Obj][rdfs.comment, "fr"] = "Médicament"
    ANNOTATIONS[Obj][rdfs.comment, "en"] = "Drug"
    assert(len(ANNOTATIONS[Obj]) == 2)
    assert(ANNOTATIONS[Obj]["comment", "fr"] == ["Médicament"])
    assert(ANNOTATIONS[Obj]["comment", "en"] == ["Drug"])

  def test_annotation3(self):
    onto = new_onto()
    class Obj(Thing): ontology = onto
    
    ANNOTATIONS[Obj].add_annotation((rdfs.comment, "fr"), "Med")
    ANNOTATIONS[Obj].add_annotation((rdfs.comment, "fr"), "Médicament")
    ANNOTATIONS[Obj].add_annotation((rdfs.comment, "en"), "Drug")
    assert(len(ANNOTATIONS[Obj]) == 3)
    assert(ANNOTATIONS[Obj]["comment", "fr"] == ["Med", "Médicament"])
    assert(ANNOTATIONS[Obj]["comment", "en"] == ["Drug"])
    
    ANNOTATIONS[Obj].del_annotation((rdfs.comment, "fr"), "Med")
    assert(len(ANNOTATIONS[Obj]) == 2)
    assert(ANNOTATIONS[Obj]["comment", "fr"] == ["Médicament"])
    assert(ANNOTATIONS[Obj]["comment", "en"] == ["Drug"])
    
    ANNOTATIONS[Obj].add_annotation((rdfs.comment, "fr"), "Med")
    del ANNOTATIONS[Obj][rdfs.comment, "fr"]
    assert(len(ANNOTATIONS[Obj]) == 1)
    assert(ANNOTATIONS[Obj]["comment", "en"] == ["Drug"])
    
  def test_annotation4(self):
    onto = new_onto()
    class Obj(Thing):               ontology = onto
    class prop(FunctionalProperty): ontology = onto
    o1 = Obj()
    o2 = Obj()
    o1.prop = o2
    
    ANNOTATIONS[o1, prop, o2][rdfs.comment] = "Test"
    assert(ANNOTATIONS[o1, prop, o2]["comment"] == ["Test"])
    
  def test_annotation5(self):
    onto = new_onto()
    class Obj(Thing):            ontology = onto
    class comment2(rdfs.comment): ontology = onto
    
    ANNOTATIONS[Obj]["comment"] = "1"
    ANNOTATIONS[Obj]["comment2"] = "2"
    assert(ANNOTATIONS[Obj]["comment"] == ["1", "2"])
    assert(ANNOTATIONS[Obj]["comment2"] == ["2"])
    
    del ANNOTATIONS[Obj]["comment"]
    assert(len(ANNOTATIONS[Obj]) == 0)
    
    
  def test_annotation6(self):
    onto = Ontology("http://test.org/test_annotations.owl").load()
    
    assert(ANNOTATIONS[onto.C]["comment", "fr"] == ["Teste !"])
    assert(ANNOTATIONS[onto.C]["comment", "en"] == ["test"])
    assert(ANNOTATIONS[onto.D, owl.is_a, onto.C]["comment"] == ["annot"])
    assert(ANNOTATIONS[onto.rel, owl.domain, onto.D]["comment"] == ["dom"])
    assert(ANNOTATIONS[onto.rel, owl.range, onto.C]["comment"] == ["range1", "range2"])
    assert(ANNOTATIONS[onto.i]["comment"] == ["ind"])
    assert(ANNOTATIONS[onto.i, owl.is_a, onto.D]["comment"] == ["ind class"])
    assert(ANNOTATIONS[onto.i, onto.rel, onto.j]["comment"] == ["ind rel"])
    
    onto.base_iri = "http://test.org/test_annotations_gen.owl"; onto.name = "test_annotations_gen"
    onto.save()
    onto.base_iri = "http://drop_it.owl"; onto.name = "drop_it"
    
    onto = Ontology("http://test.org/test_annotations_gen.owl").load() # Reload
    
    assert(ANNOTATIONS[onto.C]["comment", "fr"] == ["Teste !"])
    assert(ANNOTATIONS[onto.C]["comment", "en"] == ["test"])
    assert(ANNOTATIONS[onto.D, owl.is_a, onto.C]["comment"] == ["annot"])
    assert(ANNOTATIONS[onto.rel, owl.domain, onto.D]["comment"] == ["dom"])
    assert(ANNOTATIONS[onto.rel, owl.range, onto.C]["comment"] == ["range1", "range2"])
    assert(ANNOTATIONS[onto.i]["comment"] == ["ind"])
    assert(ANNOTATIONS[onto.i, owl.is_a, onto.D]["comment"] == ["ind class"])
    assert(ANNOTATIONS[onto.i, onto.rel, onto.j]["comment"] == ["ind rel"])

  def test_python_alias_1(self):
    onto = new_onto()
    class Obj(Thing):
      ontology = onto
    class has_for_obj(Property):
      ontology = onto
      domain   = [Obj]
      range    = [Obj]
      
    ANNOTATIONS[has_for_obj]["python_name"] = "obj"
    o = Obj()
    assert o.obj == []
    o.obj.append(Obj())
    assert len(o.obj) == 1
    assert not hasattr(o, "has_for_obj")
    
    
  def test_fusion_class1(self):
    onto = new_onto()
    class C1(Thing): ontology = onto
    class C2(Thing): ontology = onto
    
    o = C1("o")
    o.is_a.append(C2)
    assert(o.is_a == [C1, C2])
    assert(isinstance(o, C1))
    assert(isinstance(o, C2))
    assert(isinstance(o.__class__, owlready._FusionClass))
    
    o2 = o.__class__("o2")
    assert(o2.is_a == [C1, C2])
    assert(isinstance(o2, C1))
    assert(isinstance(o2, C2))
    assert(isinstance(o2.__class__, owlready._FusionClass))
    
    o.is_a.remove(C1)
    assert(o.is_a == [C2])
    assert(not isinstance(o, C1))
    assert(isinstance(o, C2))
    assert(not isinstance(o.__class__, owlready._FusionClass))
    
  def test_fusion_class2(self):
    onto = new_onto()
    class C1(Thing):
      ontology = onto
    class prop(FunctionalProperty):
      ontology = onto
      range    = [int]
    class C2(Thing):
      ontology      = onto
      equivalent_to = [restriction(prop, VALUE, 1)]
    o = C1("o")
    o.prop = 1
    
    onto.sync_reasoner()
    assert(o.is_a == [C1, C2])
    assert(isinstance(o, C1))
    assert(isinstance(o, C2))
    assert(isinstance(o.__class__, owlready._FusionClass))
    
  def test_is_functional_for1(self):
    onto = Ontology("http://www.semanticweb.org/jiba/ontologies/2014/8/test_functional_for.owl").load()
    
    assert     onto.a_pour_b.is_functional_for(onto.A1)
    assert not onto.a_pour_b.is_functional_for(onto.A2)
    
  def test_close1(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class has_for_p(Property):
      ontology = onto
      domain   = [O]
      range    = [P]
    o  = O()
    p1 = P()
    p2 = P()
    o.has_for_p = [p1, p2]
    close_world(o, [has_for_p]) # Specify the property the close, because other test may create additional properties
    
    restr = [c for c in o.is_a if not c is O][0]
    assert restr.Prop is has_for_p
    assert restr.type is ONLY
    assert isinstance(restr.Class, OneOfRestriction) and set(restr.Class.instances) == {p1, p2}
    
  def test_close2(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class Q(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
    o1 = O()
    o2 = O()
    close_world(O, [rel]) # Specify the property the close, because other test may create additional properties
    
    restr = [c for c in O.is_a if isinstance(c, OneOfRestriction)][0]
    assert set(restr.instances) == { o1, o2 }
    restr = [c for c in O.is_a if isinstance(c, NotRestriction)][0]
    restr = restr.Class
    assert restr.Prop is rel
    assert restr.type is SOME
    assert restr.Class is Thing
    
  def test_close3(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class Q(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
    p1 = P()
    p2 = P()
    q1 = Q()
    O.is_a.append(restriction(rel, VALUE, p1))
    O.is_a.append(restriction(rel, VALUE, p2))
    O.is_a.append(restriction(rel, SOME,  Q))
    close_world(O, [rel]) # Specify the property the close, because other test may create additional properties
    
    restr = O.is_a[-1]
    assert restr.Prop is rel
    assert restr.type is ONLY
    assert Q in restr.Class.Classes
    x = list(restr.Class.Classes)
    x.remove(Q)
    x = x[0]
    assert isinstance(x, OneOfRestriction) and (set(x.instances) == { p1, p2 })
    #print(O.is_a)
    
  def test_close4(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class has_for_p(Property):
      ontology = onto
      domain   = [O]
      range    = [P]
    o  = O()
    p1 = P()
    p2 = P()
    o.is_a.append(has_for_p(SOME, P))
    close_world(o, [has_for_p]) # Specify the property the close, because other test may create additional properties

    assert o.is_a[-1].Prop is has_for_p
    assert o.is_a[-1].type is ONLY
    assert o.is_a[-1].Class is P
    
  def test_close5(self):
    onto = new_onto()
    class O (Thing): ontology = onto
    class O2(O):     ontology = onto
    class P (Thing): ontology = onto
    class has_for_p(Property):
      ontology = onto
      domain   = [O]
      range    = [P]
    O.is_a.append(has_for_p(SOME, P))
    close_world(O2, [has_for_p]) # Specify the property the close, because other test may create additional properties
    
    assert O2.is_a[-1].Prop is has_for_p
    assert O2.is_a[-1].type is ONLY
    assert O2.is_a[-1].Class is P
    
  def test_close6(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class has_for_p(Property):
      ontology = onto
      domain   = [O]
      range    = [P]
    O.is_a.append(has_for_p(SOME, P))
    o = O()
    close_world(o, [has_for_p]) # Specify the property the close, because other test may create additional properties
    
    assert o.is_a[-1].Prop is has_for_p
    assert o.is_a[-1].type is ONLY
    assert o.is_a[-1].Class is P
    
  def test_close7(self):
    onto = new_onto()
    class O (Thing): ontology = onto
    class O2(O):     ontology = onto
    class P (Thing): ontology = onto
    class has_for_p(Property):
      ontology = onto
      domain   = [O]
      range    = [P]
    o = O()
    p = P()
    O2.is_a.append(has_for_p(SOME, P))
    o .has_for_p = [p]
    close_world(O, [has_for_p]) # Specify the property the close, because other test may create additional properties
    
    assert repr(O.is_a) == repr([Thing, one_of(o), has_for_p(ONLY, (P | one_of(p)))])
    
  def test_is_instance_of(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    o = O()
    assert o.is_instance_of == o.is_a
    
    o.is_instance_of.append(P)
    assert o.is_instance_of == o.is_a
    assert o.is_a == [O, P]
    
  def test_class_prop1(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
      range    = [str]
    O.is_a.append(restriction(rel, VALUE, "test"))
    assert O.rel == ["test"]
    
  def test_class_prop2(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class rel(FunctionalProperty):
      ontology = onto
      domain   = [O]
      range    = [str]
    O.is_a.append(restriction(rel, VALUE, "test"))
    assert O.rel == "test"
    
  def test_class_prop3(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class rel(FunctionalProperty):
      ontology = onto
      domain   = [O]
      range    = [str]
    O.rel = "test"
    
    assert O.is_a[-1].Prop is rel
    assert O.is_a[-1].type == VALUE
    assert O.is_a[-1].Class == "test"
    
  def test_class_prop4(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
      range    = [str]
    O.rel = "test"
    
    O.is_a.append(restriction(rel, VALUE, "a"))
    O.is_a.append(restriction(rel, VALUE, "b"))

    del O.rel
    assert O.is_a == [Thing]

  def test_class_prop5(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
      range    = [str]
      
    O.rel = ["a", "b"]

    assert len(O.is_a) == 3
    assert O.is_a[-2].Prop is rel
    assert O.is_a[-2].type == VALUE
    assert O.is_a[-1].Prop is rel
    assert O.is_a[-1].type == VALUE
    assert { O.is_a[-2].Class, O.is_a[-1].Class } == { "a", "b" }
    
    O.rel = ["a", "c"]
    
    assert len(O.is_a) == 3
    assert O.is_a[-2].Prop is rel
    assert O.is_a[-2].type == VALUE
    assert O.is_a[-1].Prop is rel
    assert O.is_a[-1].type == VALUE
    assert { O.is_a[-2].Class, O.is_a[-1].Class } == { "a", "c" }
    
  def test_class_prop6(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
      range    = [str]
      
    O.rel.append("a")
    O.rel.append("b")
    O.rel.append("c")
    O.rel.remove("b")
    
    assert len(O.is_a) == 3
    assert O.is_a[-2].Prop is rel
    assert O.is_a[-2].type == VALUE
    assert O.is_a[-1].Prop is rel
    assert O.is_a[-1].type == VALUE
    assert { O.is_a[-2].Class, O.is_a[-1].Class } == { "a", "c" }
    
  def test_class_prop7(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class rel(FunctionalProperty):
      ontology = onto
      domain   = [O]
      range    = [P]
    class inv(InverseFunctionalProperty):
      ontology = onto
      domain   = [P]
      range    = [O]
      inverse_property = rel
    p = P()
    O.rel = p
    
    assert O.is_a[-1].Prop is rel
    assert O.is_a[-1].type == VALUE
    assert O.is_a[-1].Class == p
    
    assert len(p.is_a) == 2
    assert p.is_a[-1].Prop is inv
    assert p.is_a[-1].type == SOME
    assert p.is_a[-1].Class is O
    
    
  def test_class_prop8(self):
    onto = new_onto()
    class O(Thing): ontology = onto
    class P(Thing): ontology = onto
    class rel(Property):
      ontology = onto
      domain   = [O]
      range    = [P]
    class inv(Property):
      ontology = onto
      domain   = [P]
      range    = [O]
      inverse_property = rel
    p = P()
    O.rel.append(p)
    
    assert O.is_a[-1].Prop is rel
    assert O.is_a[-1].type == VALUE
    assert O.is_a[-1].Class == p

    assert len(p.is_a) == 2
    assert p.is_a[-1].Prop is inv
    assert p.is_a[-1].type == SOME
    assert p.is_a[-1].Class is O
    
    O.rel.remove(p)
    assert len(O.is_a) == 1
    assert len(p.is_a) == 1
      
if __name__ == '__main__': unittest.main()
  

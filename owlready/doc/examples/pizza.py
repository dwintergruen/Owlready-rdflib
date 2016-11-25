
from owlready import *

#onto_path.append("./owlready/doc/examples")

pizza_onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl")
pizza_onto.load()

class NonVegetarianPizza(pizza_onto.Pizza):
  equivalent_to = [
    pizza_onto.Pizza
  & ( restriction("has_topping", SOME, pizza_onto.MeatTopping)
    | restriction("has_topping", SOME, pizza_onto.FishTopping)
    )
  ]
  
  def eat(self):
    print("Beurk! I'm vegetarian!")

test_pizza = pizza_onto.Pizza("test_pizza")

test_pizza.has_topping = [ pizza_onto.CheeseTopping(),
                           pizza_onto.TomatoTopping(),
                           pizza_onto.MeatTopping  () ]

print("Before reasoning:", test_pizza.__class__)

pizza_onto.sync_reasoner()

print("After reasoning:", test_pizza.__class__)

test_pizza.eat()

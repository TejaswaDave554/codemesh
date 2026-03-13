"""Sample Python module for testing the code analysis tool.

This module contains various functions, classes, and relationships to demonstrate
the capabilities of the code analyzer.
"""


class Animal:
    """Base animal class."""
    
    def __init__(self, name):
        """Initialize animal with name.
        
        Args:
            name: Name of the animal
        """
        self.name = name
    
    def speak(self):
        """Make the animal speak."""
        return "Some sound"
    
    def move(self):
        """Make the animal move."""
        return f"{self.name} is moving"


class Dog(Animal):
    """Dog class inheriting from Animal."""
    
    def speak(self):
        """Dog barks."""
        return "Woof!"
    
    def fetch(self, item):
        """Dog fetches an item.
        
        Args:
            item: Item to fetch
        """
        self.move()
        return f"{self.name} fetched {item}"


class Cat(Animal):
    """Cat class inheriting from Animal."""
    
    def speak(self):
        """Cat meows."""
        return "Meow!"
    
    def climb(self):
        """Cat climbs."""
        self.move()
        return f"{self.name} is climbing"


def create_animal(animal_type, name):
    """Factory function to create animals.
    
    Args:
        animal_type: Type of animal ('dog' or 'cat')
        name: Name for the animal
        
    Returns:
        Animal instance
    """
    if animal_type == 'dog':
        return Dog(name)
    elif animal_type == 'cat':
        return Cat(name)
    else:
        return Animal(name)


def make_animals_speak(animals):
    """Make multiple animals speak.
    
    Args:
        animals: List of animal instances
        
    Returns:
        List of sounds
    """
    sounds = []
    for animal in animals:
        sound = animal.speak()
        sounds.append(sound)
    return sounds


def calculate_complexity(n):
    """Function with higher complexity for testing.
    
    Args:
        n: Input number
        
    Returns:
        Calculated result
    """
    result = 0
    
    if n < 0:
        return -1
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    
    for i in range(n):
        if i % 2 == 0:
            result += i
        else:
            result -= i
        
        if result > 100:
            break
    
    while result > 50:
        result -= 10
        if result < 60:
            break
    
    return result


def recursive_fibonacci(n):
    """Recursive function example.
    
    Args:
        n: Fibonacci number position
        
    Returns:
        Fibonacci number
    """
    if n <= 1:
        return n
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)


def unused_function():
    """This function is never called."""
    return "I am unused"


def main():
    """Main entry point."""
    dog = create_animal('dog', 'Buddy')
    cat = create_animal('cat', 'Whiskers')
    
    animals = [dog, cat]
    sounds = make_animals_speak(animals)
    
    print(sounds)
    
    dog.fetch('ball')
    cat.climb()
    
    result = calculate_complexity(10)
    print(f"Complexity result: {result}")
    
    fib = recursive_fibonacci(5)
    print(f"Fibonacci: {fib}")


if __name__ == "__main__":
    main()

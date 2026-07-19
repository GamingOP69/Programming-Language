"""Create all remaining example Samrat programs."""
import os

base = os.path.join(os.path.dirname(__file__), '..', 'examples')

examples = {
    'classes.samrat': """// Samrat Classes
class Rectangle {
    let width: float
    let height: float

    constructor(width: float, height: float) {
        this.width = width
        this.height = height
    }

    func area() -> float {
        return this.width * this.height
    }

    func perimeter() -> float {
        return 2 * (this.width + this.height)
    }

    func is_square() -> bool {
        return this.width == this.height
    }
}

let rect = Rectangle(5.0, 3.0)
print("Width: " + str(rect.width))
print("Height: " + str(rect.height))
print("Area: " + str(rect.area()))
print("Perimeter: " + str(rect.perimeter()))
print("Is square? " + str(rect.is_square()))

let square = Rectangle(4.0, 4.0)
print("Square area: " + str(square.area()))
print("Square is square? " + str(square.is_square()))
""",

    'file_io.samrat': """// Samrat File I/O
let filename = "_test_output.txt"

let out = open(filename, "w")
out.write("Hello, File!")
out.write("\\nLine 2")
out.close()

let f = open(filename, "r")
let content = f.read()
print("File content:")
print(content)
f.close()

// Clean up
let clean = open(filename, "w")
clean.write("")
clean.close()
print("File I/O completed successfully!")
""",

    'error_handling.samrat': """// Samrat Error Handling
func divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero"
    }
    return a / b
}

try {
    let result = divide(10, 2)
    print("10 / 2 = " + str(result))
} catch err {
    print("Error: " + err)
}

try {
    let result = divide(10, 0)
    print("This won't print")
} catch err {
    print("Caught: " + err)
}

func safe_divide(a: int, b: int) -> int {
    try {
        return divide(a, b)
    } catch err {
        print("Division failed: " + err)
        return 0
    }
}

print("safe_divide(5, 0) = " + str(safe_divide(5, 0)))
print("safe_divide(10, 2) = " + str(safe_divide(10, 2)))
""",

    'modules.samrat': """// Samrat Modules
import math
import string

print("Math module:")
print("  sqrt(16) = " + str(math.sqrt(16)))
print("  abs(-5) = " + str(math.abs(-5)))
print("  pi = " + str(math.pi))
print("  e = " + str(math.e))
print("  pow(2, 10) = " + str(math.pow(2, 10)))
print("  floor(3.7) = " + str(math.floor(3.7)))
print("  ceil(3.2) = " + str(math.ceil(3.2)))
print("  max(10, 20) = " + str(math.max(10, 20)))
print("  min(10, 20) = " + str(math.min(10, 20)))

print("String module:")
print("  upper(hello) = " + string.upper("hello"))
print("  lower(HELLO) = " + string.lower("HELLO"))
print('  trim("  hi  ") = "' + string.trim("  hi  ") + '"')
print("  split result: " + str(string.split("a,b,c", ",")))
print("  join result: " + string.join([1, 2, 3], "-"))
print("  replace: " + string.replace("hello world", "world", "samrat"))
""",

    'calculator.samrat': """// Samrat Calculator
func add(a: int, b: int) -> int {
    return a + b
}

func subtract(a: int, b: int) -> int {
    return a - b
}

func multiply(a: int, b: int) -> int {
    return a * b
}

func divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Cannot divide by zero"
    }
    return a / b
}

func power(a: int, b: int) -> int {
    return a ** b
}

func modulo(a: int, b: int) -> int {
    return a % b
}

print("Calculator Demo:")
print("  10 + 5 = " + str(add(10, 5)))
print("  10 - 5 = " + str(subtract(10, 5)))
print("  10 * 5 = " + str(multiply(10, 5)))
print("  10 / 5 = " + str(divide(10, 5)))
print("  2 ** 10 = " + str(power(2, 10)))
print("  17 % 5 = " + str(modulo(17, 5)))

try {
    print("  10 / 0 = " + str(divide(10, 0)))
} catch err {
    print("  10 / 0 => Error: " + err)
}
""",

    'todo_app.samrat': """// Samrat Todo App
class TodoList {
    let tasks: [str]

    constructor() {
        this.tasks = []
    }

    func add(task: str) {
        this.tasks.append(task)
        print("Added: \\"" + task + "\\"")
    }

    func remove(index: int) {
        if index >= 0 and index < len(this.tasks) {
            let removed = this.tasks[index]
            this.tasks.remove(index)
            print("Removed: \\"" + removed + "\\"")
        } else {
            print("Invalid index: " + str(index))
        }
    }

    func list() {
        if len(this.tasks) == 0 {
            print("No tasks.")
        } else {
            print("Tasks:")
            for i in 0..len(this.tasks) {
                print("  " + str(i + 1) + ". " + this.tasks[i])
            }
        }
    }

    func count() -> int {
        return len(this.tasks)
    }
}

let todo = TodoList()
todo.add("Learn Samrat")
todo.add("Build something awesome")
todo.add("Write tests")
todo.list()
print("Total tasks: " + str(todo.count()))
todo.remove(1)
todo.list()
""",

    'banking_system.samrat': """// Samrat Banking System
class Account {
    let owner: str
    let balance: float

    constructor(owner: str, initial_balance: float) {
        this.owner = owner
        this.balance = initial_balance
    }

    func deposit(amount: float) {
        if amount <= 0 {
            throw "Deposit amount must be positive"
        }
        this.balance = this.balance + amount
        print("Deposited $" + str(amount) + ". New balance: $" + str(this.balance))
    }

    func withdraw(amount: float) {
        if amount <= 0 {
            throw "Withdrawal amount must be positive"
        }
        if amount > this.balance {
            throw "Insufficient funds"
        }
        this.balance = this.balance - amount
        print("Withdrew $" + str(amount) + ". New balance: $" + str(this.balance))
    }

    func get_balance() -> float {
        return this.balance
    }

    func display() {
        print("Account: " + this.owner + ", Balance: $" + str(this.balance))
    }
}

let acc = Account("Alice", 1000.0)
acc.display()
acc.deposit(500.0)
acc.withdraw(200.0)
print("Final balance: $" + str(acc.get_balance()))

try {
    acc.withdraw(2000.0)
} catch err {
    print("Error: " + err)
}
""",

    'student_management.samrat': """// Samrat Student Management
class Student {
    let name: str
    let age: int
    let grades: [int]

    constructor(name: str, age: int) {
        this.name = name
        this.age = age
        this.grades = []
    }

    func add_grade(grade: int) {
        this.grades.append(grade)
    }

    func average_grade() -> float {
        if len(this.grades) == 0 {
            return 0.0
        }
        let sum = 0
        for grade in this.grades {
            sum = sum + grade
        }
        return sum / len(this.grades)
    }

    func has_passed() -> bool {
        return this.average_grade() >= 60.0
    }

    func display() {
        print("Student: " + this.name + ", Age: " + str(this.age))
        print("  Grades: " + str(this.grades))
        print("  Average: " + str(this.average_grade()))
        if this.has_passed() {
            print("  Status: Passed")
        } else {
            print("  Status: Failed")
        }
    }
}

let students = [
    Student("Alice", 20),
    Student("Bob", 22),
    Student("Charlie", 21)
]

students[0].add_grade(85)
students[0].add_grade(90)
students[0].add_grade(78)

students[1].add_grade(55)
students[1].add_grade(60)

students[2].add_grade(95)
students[2].add_grade(88)
students[2].add_grade(92)

for student in students {
    student.display()
    print("")
}
""",

    'text_analyzer.samrat': """// Samrat Text Analyzer
func analyze_text(text: str) {
    let char_count = len(text)
    let lines = 1
    let word_count = 0
    let in_word = false

    for i in 0..char_count {
        let ch = text[i]
        if ch == "\\n" {
            lines = lines + 1
        }
        if ch != " " and ch != "\\n" and ch != "\\t" {
            if not in_word {
                word_count = word_count + 1
                in_word = true
            }
        } else {
            in_word = false
        }
    }

    print("Text Analysis:")
    print("  Characters: " + str(char_count))
    print("  Words: " + str(word_count))
    print("  Lines: " + str(lines))
}

let sample = "Hello World\\nThis is a test\\nSamrat rocks!"
print("Sample text:")
print(sample)
print("")
analyze_text(sample)
""",

    'mini_game.samrat': """// Samrat Number Guessing Game
import math

func play_game() {
    let target = 42
    let max_guesses = 7

    print("I'm thinking of a number between 1 and 100.")
    print("You have " + str(max_guesses) + " guesses.")

    let guess = 42
    print("Your guess: 42")

    if guess == target {
        print("Correct! You win!")
    } elif guess < target {
        print("Too low!")
    } else {
        print("Too high!")
    }
}

play_game()
""",

    'fizzbuzz.samrat': """// Samrat FizzBuzz
print("FizzBuzz from 1 to 30:")
for i in 1..31 {
    if i % 15 == 0 {
        print("FizzBuzz")
    } elif i % 3 == 0 {
        print("Fizz")
    } elif i % 5 == 0 {
        print("Buzz")
    } else {
        print(i)
    }
}
""",
}

for name, content in examples.items():
    path = os.path.join(base, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {name}")

print(f"\nAll {len(examples)} example files created in {base}")
import tkinter as tk

# Создаем основное окно
root = tk.Tk()
root.title("Пример сетки")

# Создаем основную сетку с двумя строками и двумя столбцами
main_grid = tk.Grid(root, column=2, row=2)

# Создаем первый фрейм и размещаем его в левом верхнем углу сетки
frame1 = tk.Frame(root, bg="blue")
frame1.grid(row=0, column=0, padx=10, pady=10)

# Создаем сетку внутри первого фрейма
frame1_grid = tk.Grid(frame1)

# Добавляем объекты в сетку фрейма
label1 = tk.Label(frame1, text="Привет, я первый фрейм!")
label1.grid(row=0, column=0)

button1 = tk.Button(frame1, text="Кнопка 1")
button1.grid(row=1, column=0)

# Создаем второй фрейм и размещаем его в правом верхнем углу сетки
frame2 = tk.Frame(root, bg="green")
frame2.grid(row=0, column=1, padx=10, pady=10)

# Создаем сетку внутри второго фрейма
frame2_grid = tk.Grid(frame2)

# Добавляем объекты в сетку фрейма
label2 = tk.Label(frame2, text="Привет, я второй фрейм!")
label2.grid(row=0, column=0)

button2 = tk.Button(frame2, text="Кнопка 2")
button2.grid(row=1, column=0)

# Запускаем главный цикл обработки событий
root.mainloop()

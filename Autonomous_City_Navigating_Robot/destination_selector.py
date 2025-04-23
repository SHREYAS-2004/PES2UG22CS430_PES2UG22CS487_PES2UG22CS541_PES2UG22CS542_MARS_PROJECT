import tkinter as tk

def write_destination(choice):
    with open("controllers/supervisor_controller/destination.txt", "w") as f:
        f.write(choice)
    selected_label.config(text=f"✅ Destination set to: {choice}")

root = tk.Tk()
root.title("Select Destination")

tk.Label(root, text="Choose Destination:").pack(pady=10)

for point in ["A", "B", "C", "D"]:
    tk.Button(root, text=f"Go to {point}", command=lambda p=point: write_destination(p)).pack(pady=5)

selected_label = tk.Label(root, text="", fg="green")
selected_label.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DissolutionTestAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dissolution Test Analysis")

        self.times = []
        self.quantities = []

        # Create GUI elements
        self.label_times = tk.Label(root, text="Time (min)")
        self.label_times.grid(row=0, column=0, padx=5, pady=5)
        self.label_quantities = tk.Label(root, text="Quantity")
        self.label_quantities.grid(row=0, column=1, padx=5, pady=5)

        self.time_entries = []
        self.quantity_entries = []

        for i in range(12):
            time_entry = tk.Entry(root)
            time_entry.grid(row=i+1, column=0, padx=5, pady=5)
            self.time_entries.append(time_entry)

            quantity_entry = tk.Entry(root)
            quantity_entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.quantity_entries.append(quantity_entry)

        self.button_fit = tk.Button(root, text="Fit to Kinetics", command=self.fit_kinetics)
        self.button_fit.grid(row=13, columnspan=2, padx=5, pady=10)

        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Quantity")
        self.ax.set_title("Dissolution Test Results and Kinetics Fit")
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=14, columnspan=2, padx=10, pady=10)

    def zero_order_kinetics(self, t, k):
        return k * t

    def first_order_kinetics(self, t, k, A0):
        return np.log(A0) - k * t

    def fit_kinetics(self):
        self.times = []
        self.quantities = []

        # Retrieve time and quantity values from the entry boxes
        for i in range(12):
            time_value = self.time_entries[i].get()
            quantity_value = self.quantity_entries[i].get()

            if time_value and quantity_value:
                self.times.append(float(time_value))
                self.quantities.append(float(quantity_value))

        if self.times and self.quantities:
            self.times = np.array(self.times)  # Convert times to numpy array

            # Perform the curve fitting for zero-order kinetics
            popt_zero, _ = curve_fit(self.zero_order_kinetics, self.times, self.quantities)
            k0 = popt_zero[0]

            # Perform the curve fitting for first-order kinetics
            popt_first, _ = curve_fit(self.first_order_kinetics, self.times, np.log(100 - np.array(self.quantities)), p0=[0.01, 100])
            k = popt_first[0]
            A0 = popt_first[1]

            # Calculate R-squared (R2) values
            r2_zero = r2_score(self.quantities, self.zero_order_kinetics(self.times, k0))
            r2_first = r2_score(np.log(100 - np.array(self.quantities)), self.first_order_kinetics(self.times, k, A0))

            # Plot the fitted curves and display R2 values
            self.ax.clear()
            self.ax.plot(self.times, self.quantities, 'o-', label="Data")
            self.ax.plot(self.times, self.zero_order_kinetics(self.times, k0), label=f"Zero-Order Kinetics (R2 = {r2_zero:.4f})")
            self.ax.plot(self.times, 100 - np.exp(self.first_order_kinetics(self.times, k, A0)), label=f"First-Order Kinetics (R2 = {r2_first:.4f})")

            # Add equation text
            zero_eq = f"y = {k0:.4f}x"
            first_eq = f"y = ln({A0:.4f}) - {k:.4f}x"
            self.ax.text(0.5, 0.5, zero_eq, transform=self.ax.transAxes, fontsize=12, va='center', ha='center',
                         bbox=dict(facecolor='white', edgecolor='gray'))
            self.ax.text(0.5, 0.4, first_eq, transform=self.ax.transAxes, fontsize=12, va='center', ha='center',
                         bbox=dict(facecolor='white', edgecolor='gray'))

            self.ax.set_xlabel("Time (min)")
            self.ax.set_ylabel("Quantity")
            self.ax.set_title("Dissolution Test Results and Kinetics Fit")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
        else:
            messagebox.showwarning("No Data", "No data available for fitting kinetics.")

if __name__ == '__main__':
    root = tk.Tk()
    gui = DissolutionTestAnalysisGUI(root)
    root.mainloop()

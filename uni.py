import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tkinter import ttk
import json
import os

class CollegeAppCountdown:
    def __init__(self, root):
        self.root = root
        self.root.title("College Application Countdown")
        self.root.geometry("1500x800")

        # Initialize the data storage
        self.colleges = []
        self.data_file = 'colleges_data.json'

        # Load existing data
        self.load_data()

        # Display today's date
        today = datetime.today().strftime('%Y-%m-%d')
        self.today_label = tk.Label(self.root, text=f"Today's Date: {today}", font=('Arial', 14))
        self.today_label.pack(pady=10)

        # Buttons frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=5)

        # Button to add a new college application
        self.add_button = tk.Button(buttons_frame, text="Add College Application", command=self.add_college, width=20)
        self.add_button.pack(side='left', padx=5)

        # Button to edit selected college application
        self.edit_button = tk.Button(buttons_frame, text="Edit Selected", command=self.edit_college, width=15)
        self.edit_button.pack(side='left', padx=5)

        # Button to delete selected college application
        self.delete_button = tk.Button(buttons_frame, text="Delete Selected", command=self.delete_college, width=15)
        self.delete_button.pack(side='left', padx=5)

        # Button to unselect any selection
        self.unselect_button = tk.Button(buttons_frame, text="Unselect", command=self.unselect_item, width=10)
        self.unselect_button.pack(side='left', padx=5)

        # Create a treeview to display the colleges
        columns = ('University Name', 'Supplemental Essays', 'Deadline', 'Application Type', 'Days Left', 'Essay Completed', 'Application Submitted')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', selectmode='browse')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor='center')

        # Vertical scrollbar for the treeview
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(pady=10, fill='both', expand=True)

        # Create tags for alternating row colors
        self.tree.tag_configure('evenrow', background='#f0f0f0')
        self.tree.tag_configure('oddrow', background='#ffffff')

        # Bind the window close event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind double-click event on checkboxes
        self.tree.bind('<Double-1>', self.on_double_click)

        self.refresh_tree()

    def add_college(self):
        self.open_college_window()

    def open_college_window(self, edit=False, index=None):
        # Create a new window to add or edit college details
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Edit College Application" if edit else "Add College Application")
        self.new_window.geometry("450x280")

        tk.Label(self.new_window, text="University Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.university_entry = tk.Entry(self.new_window, width=25)
        self.university_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.new_window, text="Supplemental Essays:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.essays_entry = tk.Entry(self.new_window, width=25)
        self.essays_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.new_window, text="Deadline (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.deadline_entry = tk.Entry(self.new_window, width=25)
        self.deadline_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.new_window, text="Application Type (RD/ED/EA):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.type_entry = tk.Entry(self.new_window, width=25)
        self.type_entry.grid(row=3, column=1, padx=5, pady=5)

        # Checkboxes for essay completed and application submitted
        self.essay_var = tk.BooleanVar()
        self.submitted_var = tk.BooleanVar()

        tk.Checkbutton(self.new_window, text="Essay Completed", variable=self.essay_var).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        tk.Checkbutton(self.new_window, text="Application Submitted", variable=self.submitted_var).grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Save button
        action_text = "Update" if edit else "Add"
        tk.Button(self.new_window, text=action_text, command=lambda: self.save_college(edit, index), width=10).grid(row=6, column=0, columnspan=2, pady=10)

        # If editing, pre-populate the fields with existing data
        if edit and index is not None:
            college = self.colleges[index]
            self.university_entry.insert(0, college['name'])
            self.essays_entry.insert(0, college['essays'])
            self.deadline_entry.insert(0, college['deadline'])
            self.type_entry.insert(0, college['app_type'])
            self.essay_var.set(college.get('essay_completed', False))
            self.submitted_var.set(college.get('app_submitted', False))

    def save_college(self, edit=False, index=None):
        name = self.university_entry.get()
        essays = self.essays_entry.get()
        deadline_str = self.deadline_entry.get()
        app_type = self.type_entry.get().upper()
        essay_completed = self.essay_var.get()
        app_submitted = self.submitted_var.get()

        # Validate inputs
        if not name or not essays or not deadline_str or not app_type:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            essays = int(essays)
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            if app_type not in ['RD', 'ED', 'EA']:
                raise ValueError("Application Type must be RD, ED, or EA.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        days_left = (deadline.date() - datetime.today().date()).days

        college = {
            'name': name,
            'essays': essays,
            'deadline': deadline_str,  # Save as string for JSON serialization
            'app_type': app_type,
            'days_left': days_left,
            'essay_completed': essay_completed,
            'app_submitted': app_submitted
        }

        if edit and index is not None:
            self.colleges[index] = college
        else:
            self.colleges.append(college)

        self.refresh_tree()
        self.save_data()
        self.new_window.destroy()

    def refresh_tree(self):
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort colleges by deadline and name
        self.colleges.sort(key=lambda x: (x['deadline'], x['name']))

        # Recalculate days left
        for college in self.colleges:
            deadline = datetime.strptime(college['deadline'], '%Y-%m-%d')
            college['days_left'] = (deadline.date() - datetime.today().date()).days

        # Insert colleges into the tree with alternating row colors
        for idx, college in enumerate(self.colleges):
            essay_status = 'YES' if college.get('essay_completed', False) else 'NO'
            app_status = 'YES' if college.get('app_submitted', False) else 'NO'

            # Assign tag based on even or odd row
            row_tag = 'evenrow' if idx % 2 == 0 else 'oddrow'

            self.tree.insert('', 'end', iid=idx, values=(
                college['name'],
                college['essays'],
                college['deadline'],
                college['app_type'],
                college['days_left'],
                essay_status,
                app_status
            ), tags=(row_tag,))

    def on_double_click(self, event):
        # Identify the item clicked on
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id:
            return

        index = int(item_id)
        college = self.colleges[index]

        # Check which column was double-clicked
        if column == '#6':  # Essay Completed Column
            college['essay_completed'] = not college.get('essay_completed', False)
        elif column == '#7':  # Application Submitted Column
            college['app_submitted'] = not college.get('app_submitted', False)
        else:
            return  # Do nothing if other columns are clicked

        self.refresh_tree()
        self.save_data()

    def delete_college(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Delete Warning", "Please select an item to delete.")
            return

        item_id = selected_item[0]
        index = int(item_id)

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected college application?")
        if confirm:
            self.colleges.pop(index)
            self.refresh_tree()
            self.save_data()

    def edit_college(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Edit Warning", "Please select an item to edit.")
            return

        item_id = selected_item[0]
        index = int(item_id)

        self.open_college_window(edit=True, index=index)

    def unselect_item(self):
        # Unselect any selected item
        self.tree.selection_remove(self.tree.selection())

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def save_data(self):
        # Save colleges list to a JSON file
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.colleges, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    def load_data(self):
        # Load colleges list from a JSON file if it exists
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.colleges = json.load(f)
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not load data: {e}")
                self.colleges = []
        else:
            self.colleges = []

def main():
    root = tk.Tk()
    app = CollegeAppCountdown(root)
    root.mainloop()

if __name__ == "__main__":
    main()

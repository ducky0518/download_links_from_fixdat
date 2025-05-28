import customtkinter as ctk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import os

class RomDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Download Link Creator from fixDAT (by -God-like)")
        self.geometry("550x600") # Adjusted height for new button

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.dat_file_path = ""
        self.rom_data = [] # To store (rom_name, game_name) tuples

        # Define status colors
        self.color_success = "green"
        self.color_error = "red"
        self.color_warning = "#FF8C00" # DarkOrange
        _dummy_label = ctk.CTkLabel(self, text="test") # To get default theme color
        self.color_info = _dummy_label.cget("text_color")
        _dummy_label.destroy()

        # --- UI Elements ---

        # File Selection Frame
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=10, fill="x")
        self.file_label = ctk.CTkLabel(self.file_frame, text="No DAT File Selected")
        self.file_label.pack(side="left", padx=5, expand=True, fill="x")
        self.browse_button = ctk.CTkButton(self.file_frame, text="Browse DAT File", command=self.browse_file)
        self.browse_button.pack(side="right", padx=5)

        # Name Type Selection Frame
        self.name_type_frame = ctk.CTkFrame(self)
        self.name_type_frame.pack(pady=10, padx=10, fill="x")

        self.name_type_display_label = ctk.CTkLabel(self.name_type_frame, text="Name Source:") # Changed label
        self.name_type_display_label.pack(side="left", padx=(5,10))

        self.name_selection_var = ctk.StringVar(value="Game Name") # Default to Game Name
        self.name_type_segmented_button = ctk.CTkSegmentedButton(
            self.name_type_frame,
            values=["Rom Name", "Game Name"],
            command=self.update_name_type_display,
            variable=self.name_selection_var
        )
        self.name_type_segmented_button.pack(side="left", padx=5, expand=True, fill="x")
        self.name_type_segmented_button.set("Game Name") # Ensure default is selected visually


        # URL Input Frame
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.pack(pady=10, padx=10, fill="x")
        self.url_label = ctk.CTkLabel(self.url_frame, text="Base URL:")
        self.url_label.pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="e.g., http://mysite.com/downloads")
        self.url_entry.pack(side="right", padx=5, fill="x", expand=True)

        # File Extension Input Frame
        self.ext_frame = ctk.CTkFrame(self)
        self.ext_frame.pack(pady=10, padx=10, fill="x")
        self.ext_label = ctk.CTkLabel(self.ext_frame, text="File Extension:")
        self.ext_label.pack(side="left", padx=5)
        self.ext_entry = ctk.CTkEntry(self.ext_frame, placeholder_text="e.g., .zip")
        self.ext_entry.pack(side="right", padx=5, fill="x", expand=True)

        # Action Buttons Frame
        self.action_buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_buttons_frame.pack(pady=20, padx=10, fill="x")

        self.generate_button = ctk.CTkButton(self.action_buttons_frame, text="Generate & Save List", command=self.generate_and_save_list)
        self.generate_button.pack(side="left", padx=(0,5), expand=True, fill="x")

        self.copy_button = ctk.CTkButton(self.action_buttons_frame, text="Copy List to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side="right", padx=(5,0), expand=True, fill="x")

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Welcome! Select a DAT file to begin.", wraplength=500)
        self.status_label.pack(pady=10, padx=10, fill="x")
        self.status_label.configure(text_color=self.color_info)

    def update_name_type_display(self, selected_value: str):
        # The segmented button's variable (self.name_selection_var) is automatically updated.
        # This function is mostly for any additional actions upon selection, like updating status.
        self.status_label.configure(text=f"Name source set to: {selected_value}", text_color=self.color_info)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select RomVault FixDat File",
            filetypes=(("DAT files", "*.dat"), ("XML files", "*.xml"), ("All files", "*.*"))
        )
        if file_path:
            self.dat_file_path = file_path
            display_name = os.path.basename(file_path)
            if len(display_name) > 30: display_name = "..." + display_name[-27:]
            self.file_label.configure(text=display_name)
            self.status_label.configure(text="DAT file loaded. Attempting to parse...", text_color=self.color_info)
            self.parse_dat_file()
        else:
            self.file_label.configure(text="No DAT File Selected")
            self.status_label.configure(text="File selection cancelled.", text_color=self.color_info)
            self.rom_data = []

    def parse_dat_file(self):
        if not self.dat_file_path:
            self.status_label.configure(text="Error: No DAT file path for parsing.", text_color=self.color_error)
            return

        self.rom_data = []
        try:
            tree = ET.parse(self.dat_file_path)
            root = tree.getroot()
            for game_element in root.findall('.//game'):
                game_name_attr = game_element.get('name')
                rom_name_attr = None
                rom_element = game_element.find('rom')
                if rom_element is not None: rom_name_attr = rom_element.get('name')
                
                final_game_name = game_name_attr if game_name_attr else rom_name_attr
                final_rom_name = rom_name_attr if rom_name_attr else game_name_attr

                if final_game_name: # Prioritize game name presence
                     self.rom_data.append((final_rom_name if final_rom_name else final_game_name, final_game_name))

            if not self.rom_data:
                for rom_element in root.findall('.//rom'):
                    rom_name = rom_element.get('name')
                    if rom_name: self.rom_data.append((rom_name, rom_name))
            
            if not self.rom_data:
                self.status_label.configure(text="No game/rom entries found. Check DAT format or content.", text_color=self.color_warning)
                messagebox.showwarning("Parsing Warning", "Could not find recognizable game or rom entries.")
                return
            self.status_label.configure(text=f"Successfully parsed {len(self.rom_data)} entries.", text_color=self.color_info)
        except ET.ParseError as e:
            messagebox.showerror("Parsing Error", f"Failed to parse DAT file (not valid XML?):\n{e}")
            self.status_label.configure(text="Error parsing DAT file.", text_color=self.color_error)
            self.rom_data = []
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error during parsing: {e}")
            self.status_label.configure(text=f"Parsing Error: {e}", text_color=self.color_error)
            self.rom_data = []

    def _generate_url_list_data(self) -> list[str] | None:
        """
        Helper function to perform checks and generate the list of URL strings.
        Returns a list of URLs or None if a critical error occurs.
        Returns an empty list if no URLs could be generated but no critical error.
        """
        if not self.dat_file_path:
            messagebox.showerror("Error", "Please select and parse a DAT file first.")
            self.status_label.configure(text="Action failed: No DAT file selected.", text_color=self.color_warning)
            return None
        if not self.rom_data:
            messagebox.showerror("Error", "No ROM data loaded. Parse a DAT file, or it might be empty/unsupported.")
            self.status_label.configure(text="Action failed: No ROM data available.", text_color=self.color_warning)
            return None

        base_url = self.url_entry.get().strip()
        if not base_url:
            messagebox.showerror("Error", "Please enter a base URL.")
            self.status_label.configure(text="Action failed: Base URL is required.", text_color=self.color_warning)
            return None

        file_extension = self.ext_entry.get().strip()
        if file_extension and not file_extension.startswith('.'):
            file_extension = "." + file_extension

        url_list = []
        name_source_choice = self.name_selection_var.get() # "Rom Name" or "Game Name"

        for entry_rom_name, entry_game_name in self.rom_data:
            name_to_use = None
            if name_source_choice == "Rom Name":
                name_to_use = entry_rom_name
            else: # "Game Name"
                name_to_use = entry_game_name
            
            # Fallback if preferred name is missing but the other exists
            if not name_to_use:
                if name_source_choice == "Rom Name" and entry_game_name:
                    name_to_use = entry_game_name
                elif name_source_choice == "Game Name" and entry_rom_name:
                    name_to_use = entry_rom_name
            
            if name_to_use:
                url_safe_name = name_to_use.replace(" ", "%20")
                download_url = f"{base_url.rstrip('/')}/{url_safe_name}{file_extension}"
                url_list.append(download_url)

        if not url_list:
            self.status_label.configure(text="No URLs generated. Check DAT content or name selection.", text_color=self.color_warning)
            messagebox.showwarning("Info", "No URLs were generated. This could be due to missing names in the DAT for the selected type, or an empty/filtered DAT.")
            return [] # Return empty list, not None, as it's not a blocking error

        return url_list

    def generate_and_save_list(self):
        download_list = self._generate_url_list_data()

        if download_list is None: # Critical error occurred, already handled
            return
        if not download_list: # No URLs generated, message already shown
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            title="Save Download List As"
        )

        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    for url in download_list:
                        f.write(url + "\n")
                self.status_label.configure(
                    text=f"Download list saved to: {os.path.basename(save_path)}",
                    text_color=self.color_success
                )
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save the file: {e}")
                self.status_label.configure(text=f"Error saving file: {e}", text_color=self.color_error)
        else:
            self.status_label.configure(text="Save operation cancelled.", text_color=self.color_info)

    def copy_to_clipboard(self):
        download_list = self._generate_url_list_data()

        if download_list is None: # Critical error occurred, already handled
            return
        if not download_list: # No URLs generated, message already shown
            return

        try:
            self.clipboard_clear()
            self.clipboard_append("\n".join(download_list))
            self.status_label.configure(
                text=f"{len(download_list)} URLs copied to clipboard!",
                text_color=self.color_success
            )
        except Exception as e: # Should be rare with Tkinter's clipboard
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}")
            self.status_label.configure(text=f"Clipboard error: {e}", text_color=self.color_error)


if __name__ == "__main__":
    app = RomDownloaderApp()
    app.mainloop()
import numpy as np
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from tkinter import *
from tkinter import filedialog, simpledialog, Button
from tkinter.filedialog import askopenfilename, askdirectory, askopenfilenames
import nd2
from nd2reader import ND2Reader
import tifffile
from tifffile import imwrite
import dask
import dask.array as da




def load_img(filepath, channelcount, attributes):

    # print('channel count is:', channelcount)
    print('attributes:', attributes)
    # print('filepath:', filepath)
        
    # file_path = filedialog.askopenfilenames()
    # extension=pathlib.Path(file_path[0]).suffix
    # print(extension)
    

    # # folder_name=os.path.dirname(file_path[0])
    fig, (ax, ax_slider) = plt.subplots(2,1, figsize=(16,9), gridspec_kw={'height_ratios': [20, 1]})

    # file_in= nd2.ND2File(filepath)
    # file=np.asarray(file_in)
    # print(file_in.metadata)
    # file_in.close()


    grid=nd2.imread(filepath, dask=True)
    grid=grid[:, int(channelcount)-1, :, :]
    # grid=da.swapaxes(grid, 0, 1)
    print('shape of grid is', np.shape(grid))

    slider = Slider(ax_slider, label="val", valmin=0, valmax=np.shape(grid)[0], valstep=1)
    # add a button to export the image
    ax_export= plt.axes([0.8, 0.2, 0.1, 0.1])
    button_export= matplotlib.widgets.Button(ax_export, 'Export Image')
    

    def func_export_image(event):
        # export the image
        print('Exporting image')
        # ask the user to select the folder to save the image
        folder_path = askdirectory()
        print('folder_path:', folder_path)
        # save the image as npy file
        np.save(os.path.join(folder_path, 'exported_image.npy'), grid.compute())

        # if yes
        if messagebox.askyesno("Information", "Do you want to save file as tiff?"):
            # save the image as a series of tiff files
            for i in range(np.shape(grid)[0]):
                imwrite(os.path.join(folder_path, f'exported_image_{i}.tiff'), grid.compute())
            # imwrite(os.path.join(folder_path, 'exported_image.tiff'), grid.compute())
            # show a message box
            messagebox.showinfo("Information", "Image exported successfully")

    button_export.on_clicked(func_export_image)


    def visualize(val):
        # image=np.where(grid[slider.val,  :, :]>=slider_tol.val, grid[slider.val,  :, :], 0)
        
        ax.imshow(grid[slider.val,  :, :])
    
    slider.on_changed(visualize)
    plt.show()

    # if 

def on_submit():
    Channel_count = entry.get()
    print("Channel Count User Input:", Channel_count)
    # You can use the user input here, for example, to load an image
    # load_img(user_input)
    load_img(filepath, Channel_count, attributes)
    # close the window
    root.destroy()




if __name__ == '__main__':
    import nd2
    from tkinter import ttk, filedialog, messagebox
    import json



    root = Tk()
    root.title("ND2 Viewer")

    messagebox.showinfo("Information", "Select an ND2 file to visualize")



    # Ask the user to select an ND2 file
    filepaths = filedialog.askopenfilenames(filetypes=[("ND2 files", "*.nd2")])
    
    if filepaths:
        filepath = filepaths[0]  # Select the first file from the tuple
        print(filepath)
        
        with nd2.ND2File(filepath) as nd2_file:

            # Check with other files
            attributes = nd2_file.attributes
            print('attributes:', attributes)

            # Get all available attributes 
            all_attributes = {attr: getattr(attributes, attr) for attr in dir(attributes) if not callable(getattr(attributes, attr)) and not attr.startswith("__")}
            print('All available attributes:', all_attributes)



            attributes_dict = {
                'channelCount': attributes.channelCount,
                'width': attributes.widthPx,
                'height': attributes.heightPx,
                'z_levels': attributes.sequenceCount,
            # Add other attributes as needed
            }
            # Convert dictionary to string
            attributes_str = json.dumps(attributes_dict, indent=4)
        

            print("Channel Count:", attributes.channelCount)

        # Create an Entry widget
        Label(root, text="Detail of the nd2 image file:").pack(pady=5)
        tree = ttk.Treeview(root, columns=("Attribute", "Value"), show='headings')
        tree.heading("Attribute", text="Attribute")
        tree.heading("Value", text="Value")
        tree.pack(pady=5)

        # Insert the attributes into the Treeview
        for key, value in all_attributes.items():
            tree.insert("", "end", values=(key, value))


        entry_label = Label(root, text="Enter Channel Number:")
        entry_label.pack(pady=5)

        entry = Entry(root)
        entry.pack(pady=5)
        # Put 1 if it is only one channel
        if attributes.channelCount == 1:
            entry.insert(0, "1")

            # Create a Submit button
        submit_button = Button(root, text="Submit", command=on_submit)
        submit_button.pack(pady=5)
        

        root.mainloop()
            
            
            



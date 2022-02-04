# Description of the Database

### 1. TABLENAME    PROJECT
 
**FUNCTION**

The current organism being finished

**COLUMNS**    
* **project_id:**   		Unique identifier for the project
* **main_project_id:**		If this is a subproject, the id of the main project it is associated with another project.
* **name:**         		The short name of the project (used to name files, ...)
* **full_name:**   		The full name for the project (human interpertable)
* **type:**			    An enumerated set, descriptive of the project type

### 2. TABLENAME    PLATE

**FUNCTION**   

A physical plate of any kind.

**COLUMNS**    
* **Inc_ID:**	        A Unique identifier for the plate\n
* **Type:**		    The type of plate:
    - assay
    - source
* **Process_status:**  Where the plate is in the sequencing process
* **Barcode:**		    barcode for the plate
* **Exp_ID:**		    Experiment ID (Curently file name)
* **Format:**    	    The number of wells (96 or 384). MUST NOT BE NULL.
* **Date_created:** 	First recording date of the plate information
* **Time_created:** 	First recording time of the plate information
* **Control_QC:**      Either "Pass" or "Fail".
* **Exp_Image:**       Experiment image in BLOB format
* **Name:**		    name string for the plate
* **Origin:**	  	    The original source: pgf, lanl, llnl...

### 3. TABLENAME    PLATE_QUALITY
 
**FUNCTION**

Tracks the quality for each plate.

**COLUMNS**    
* **plate_id:**       References a record in the plate table
* **type:**	       The type of quality being tracked
* **value:**		   The quality value

### 4.  (Incomplete) TABLENAME   SOURCE_PLATE

**FUNCTION**  

The plates containing libraries of dna to be used in finishing a project.

**COLUMNS**    
* **plate_id:**     	Unique identifier for this plate
* **type:**		the type of source plate
* **well:**		the well id
* **location_serial_num:**
* **availability**:  	Indicates status of the plate - available, unusable...

### 5. TABLENAME	assay_plate
 
**FUNCTION**
    
The plates containing a treatment condition being measured. Think AMR, it's the plate that we take absorbance readings on.

**COLUMNS:**

* **Inc_ID:**         A Unique identifier for the plate
* **Data_group:**	    Group of the data (Experimental or Control)
* **Row_num:**	    Row number for indexing 
* **Well:**	        The well id
* **Raw_Value:** 		Raw value
* **Elapsed_time:**	Readings at different timepoints
* **Data_File_Name:**	Experiment data file name
* **Reading_date:**	Plate reading date
* **Reading_time:**	Plate reading time
* **Assay_Details:** 	Details of the assay. For example Raw OD(590)
* **Blank_Adj_Value:** Blank adjusted data
* **Type:**	        The type of assay, for example dose_response
* **Sample:**          The sample in the well, ideally comes from the source plate and is an ID, but for now we'll just use the sample name.
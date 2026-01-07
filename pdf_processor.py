import tabula
import pandas as pd
import re
import os
import traceback
# Setting the path to the Java installation.
os.environ["JAVA_HOME"] = r"C:\Program Files\Java\jdk-22"
os.environ["PATH"] = os.environ["JAVA_HOME"] + r"\bin;" + os.environ["PATH"]

def extract_and_clean_url(text):
    if pd.isna(text):
        return "", ""

    text = str(text).replace('\r', ' ').replace('\n', ' ')

    match = re.search(r'(https?://\S+)', text)

    if match:
        url_part = match.group(1).strip()
        title_part = text.replace(url_part, "").strip()

        #  fallback: if no title, use URL
        if not title_part:
            title_part = url_part

        clickable_url = f'=HYPERLINK("{url_part}", "{url_part}")'
        return title_part, clickable_url

    return text, ""



def process_all_pdfs(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    master_list = []
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    print(f"Found {len(pdf_files)} PDF files. Starting batch process...")

    for filename in pdf_files:
        input_path = os.path.join(input_folder, filename)
        individual_csv_name = filename.replace('.pdf', '.csv')
        individual_csv_path = os.path.join(output_folder, individual_csv_name)

        print(f"--- Processing: {filename} ---")
        
        try:
            # Using lattice=True as per your original script
            # New robust version (no JPype needed)
            tables = tabula.read_pdf(
                          input_path, 
                          pages='all', 
                          lattice=True, 
                          multiple_tables=True,
                          java_options=["-Dfile.encoding=UTF8", "-Xmx2G"] # Forces UTF8 and gives Java 2GB of RAM
                          
               )
            file_data = []
            target_columns = ['DA', 'Source', 'Target', 'Indexed']

            for df in tables:
                df = df.dropna(how='all').dropna(axis=1, how='all')
                if len(df.columns) >= 4:
                    df = df.iloc[:, :4]
                    df.columns = target_columns
                    
                    #  logic to separate Source into Title and URL Only
                    # This creates a tuple (Title, URL)
                    temp_source = df['Source'].apply(extract_and_clean_url)
                    temp_target=df['Target'].apply(extract_and_clean_url)
                    
                    # Split the tuple into two separate columns
                    df['Source'] = temp_source.apply(lambda x: x[0])
                    df['Source_url'] = temp_source.apply(lambda x: x[1])

                    #split the tuple into two separate columns for Target as well  
                    df['Target'] = temp_target.apply(lambda x: x[0])
                    df['Target_url'] = temp_target.apply(lambda x: x[1])  
                    # Filter for rows that have a number in DA
                    df = df[df['DA'].astype(str).str.contains(r'\d', na=False)]
                    file_data.append(df)

            if file_data:
                individual_df = pd.concat(file_data, ignore_index=True)
                
                # Reorder columns to put URL Only at the end
                final_cols = ['DA', 'Source', 'Target', 'Indexed', 'Source_url', 'Target_url']
                individual_df = individual_df[final_cols]
                
                individual_df.to_csv(individual_csv_path, index=False, encoding='utf-8-sig')
                master_list.append(individual_df)
                print(f"Saved individual CSV: {individual_csv_name}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            traceback.print_exc()

    if master_list:
        combined_df = pd.concat(master_list, ignore_index=True)
        combined_path = os.path.join(output_folder, "ALL_BACKLINKS_COMBINED.csv")
        combined_df.to_csv(combined_path, index=False, encoding='utf-8-sig')
        print(f"\n ALL DONE! ")
        print(f"Master file saved at: {combined_path}")


if __name__ == "__main__":
    process_all_pdfs("Backlinks", "cleaned_outputs")

import zstandard as zstd
import io
import re
import argparse
import numpy as np

def match_regex_bool(line, regex):
    return bool(regex.match(line))

def match_regex(conf_line,regex):
    return regex.findall(conf_line)

def get_formatted_confnames(list_file, conf_regex):
    confignames = []
    for unformatted_configname in np.loadtxt(list_file, dtype=str):
        confignames.append(match_regex(unformatted_configname, conf_regex))
    return confignames

def remove_measurements(fin, fout, list_file, regex_begin, regex_end, regex_conf):

    confignames_to_remove = get_formatted_confnames(list_file, regex_conf)
    print("Formatted config names", confignames_to_remove)
    
    with open(input_file, "rb") as fin, zstd.open(output_file, "w") as fout:
    
        dctx = zstd.ZstdDecompressor()  

        with dctx.stream_reader(fin) as reader:

            text_stream = io.TextIOWrapper(reader, encoding="utf-8")

            writing_mode = False
            config_name = None

            metadata_buffer = [] # For when we have to write the metadata for a config after we removed the previous one 

            for line in text_stream:

                metadata_buffer.append(line)
                
                if match_regex_bool(line, regex_begin):
                    
                    print("Found beginning of config", line)
                    config_name = match_regex(line, regex_conf)

                    if config_name in confignames_to_remove:
                        print("This configuration is not meant to be here, passing")
                        fout.write("-- A measurement was here but was removed by remove_measurements.py --\n")
                        writing_mode = False
                    else:
                        writing_mode = True
                        # Write metadata left behind
                        for l in metadata_buffer:
                            fout.write(l)

                    continue # Skip rest of loop to avoid double writing the begin regex line 
                
                if writing_mode:
                    fout.write(line)
                
                if match_regex_bool(line, regex_end):
                    print("End of configuration, disabling writing mode ")
                    writing_mode = False
                    metadata_buffer = []

def parse_args():
    parser = argparse.ArgumentParser(description="Remove select measurements from raw log HiRep files")
    parser.add_argument("--input_file", type=str, required=True, help="Input ztsd log files")
    parser.add_argument("--output_file", type=str, required=True, help="Output file name")
    parser.add_argument("--list_file", type=str, required=True, help="Configurations to skip")  
    args = parser.parse_args()
    return args

if __name__ == "__main__":

    args = parse_args()
    
    input_file = args.input_file
    output_file = args.output_file
    list_file = args.list_file

    regex_begin = re.compile("\[IO\]\[0\]Configuration")
    regex_end = re.compile("\[MAIN\]\[0\]Configuration #[0-9]*: analysed in \[.*\]")
    regex_conf = re.compile("\/run[0-9]*_[0-9]*x[0-9]*x[0-9]*x[0-9]*nc[0-9]b[^\/].*n[0-9]*")

    remove_measurements(input_file, output_file, list_file, regex_begin, regex_end, regex_conf)
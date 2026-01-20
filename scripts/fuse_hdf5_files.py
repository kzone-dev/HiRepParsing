import h5py as h5
import re
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Fuse HDF5 files containing connected and disconnected spectra data.')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing the HDF5 files.')
    parser.add_argument('--output_file', type=str, required=False, help='Output HDF5 file name.')
    args = parser.parse_args()
    return args.data_dir, args.output_file
    
data_dir, output_hdf5 = parse_args()
ensembles = ['M3', 'M4']
reps = ["AS", "FUN"]
connectedness = ['conn', 'disc']

for ensemble in ensembles:
    for rep in reps:
        # Use bigger file to append to
        disc_file = os.path.join(data_dir, f'{ensemble}_{rep}_disc_spectrum.hdf5')
        conn_file = os.path.join(data_dir, f'{ensemble}_{rep}_conn_spectrum.hdf5')

        with h5.File(disc_file, 'a') as disc_h5, h5.File(conn_file, 'r') as conn_h5:
            print("Keys in disc file: ", disc_h5[ensemble].keys())
            print("Keys in conn file: ", conn_h5[ensemble].keys())

            for key in conn_h5[ensemble].keys():
                if key not in disc_h5[ensemble].keys():
                    print("Need to write: ", key, "into disc file")
                    conn_h5[ensemble].copy(key, disc_h5[ensemble])
                else:
                    print("Key already exists: ", key)


conn_type = {
    'CONN': r"source_N[0-9]+_sink_N[0-9]+ TRIPLET",
    'DISC': r"DISCON_SEMWALL smear_N[0-9]+ SINGLET"
}

for ensemble in ensembles:
    for rep in reps:

        filename = os.path.join(data_dir, f"{ensemble}_{rep}_disc_spectrum.hdf5")
        input_file = h5.File(filename, 'r')
        output_file = h5.File(output_hdf5, 'a')

        #for ctype, pattern in conn_type.items():

        for key in input_file[ensemble].keys():

            reg_match = False

            if re.match(conn_type['CONN'], key):
                ctype = "CONN"
                h5group_path = f"/{ensemble}/{rep}/{ctype}"
                reg_match = True
            elif re.match(conn_type['DISC'], key):
                ctype = "DISC"
                h5group_path = f"/{ensemble}/{rep}/{ctype}"
                reg_match = True

            if reg_match:
                output_group = output_file.require_group(h5group_path)
                print(f"Copying",input_file[ensemble], key, f"to {h5group_path}...")
                input_file.copy(f"{ensemble}/{key}", output_group)
            else:
                print(f"Key {key} does not match any known pattern.")
                print(f"Must be parameter key, copying to both... ")
                for ctype in conn_type.keys():
                    h5group_path = f"/{ensemble}/{rep}/{ctype}"
                    output_group = output_file.require_group(h5group_path)
                    input_file.copy(f"{ensemble}/{key}", output_group)

import re
import h5py
ensembles = ['M3', 'M4']
reps = ["AS", "FUN"]

conn_type = {
    'CONN': r"source_N[0-9]+_sink_N[0-9]+ TRIPLET",
    'DISC': r"DISCON_SEMWALL smear_N[0-9]+ SINGLET"
}

output_hdf5 = "/users/nrebelobrito/flavour_singlet_and_glueball_mixing_sp4/parsed_ferm_data/singlets_smeared.hdf5"

for ensemble in ensembles:
    for rep in reps:

        filename = f"/users/nrebelobrito/flavour_singlet_and_glueball_mixing_sp4/parsed_ferm_data/{ensemble}_{rep}_disc_spectrum.hdf5"
        input_file = h5py.File(filename, 'r')
        output_file = h5py.File(output_hdf5, 'a')

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

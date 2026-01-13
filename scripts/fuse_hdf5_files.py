import h5py as h5

ensembles = ['M3', 'M4']
reps = ["AS", "FUN"]
connectedness = ['conn', 'disc']

for ensemble in ensembles:
    for rep in reps:
        # Use bigger file to append to
        disc_file = f'{ensemble}_{rep}_disc_spectrum.hdf5'
        conn_file = f'{ensemble}_{rep}_conn_spectrum.hdf5'

        with h5.File(disc_file, 'a') as disc_h5, h5.File(conn_file, 'r') as conn_h5:
            print("Keys in disc file: ", disc_h5[ensemble].keys())
            print("Keys in conn file: ", conn_h5[ensemble].keys())

            for key in conn_h5[ensemble].keys():
                if key not in disc_h5[ensemble].keys():
                    print("Need to write: ", key, "into disc file")
                    conn_h5[ensemble].copy(key, disc_h5[ensemble])
                else:
                    print("Key already exists: ", key)



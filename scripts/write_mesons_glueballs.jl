# Regex based parsing for meson measurements

using Pkg; Pkg.activate("."); Pkg.instantiate()
using HiRepParsing
using HDF5
using DelimitedFiles

Pkg.add("ArgParse")
using ArgParse

Pkg.add("CSV")
Pkg.add("DataFrames")
using CSV
using DataFrames

function parse_commandline()
    s = ArgParseSettings()
    @add_arg_table s begin
        "--output_dir"
            help = "Path to the output directory."
            required = true
        "--ensemble"
            help = "Ensemble name to process."
            required = true
        "--meson_measurements_metadata"
            help = "Path to the metadata file containing meson measurements information."
            required = true
    end
    return parse_args(s)
end

args = parse_commandline()
output_dir = args["output_dir"]
ensemble = args["ensemble"]
meson_measurements_metadata = args["meson_measurements_metadata"]

function main(h5file;ensemble,rep,disc,nhits,file,setup=true,filter_channels=false,channels=nothing)
    #isfile(h5file) && rm(h5file)
    if disc == "DISC"
        smearing_regex = r"DISCON_SEMWALL smear_N[0-9]+ SINGLET"
        h5group = joinpath(ensemble,rep,disc)
        writehdf5_spectrum_disconnected_with_regexp(file,h5file,smearing_regex,nhits;mixed_rep=false,h5group=h5group,setup,filter_channels,channels,sort=true,deduplicate=true)
    else
        smearing_regex = r"source_N[0-9]+_sink_N[0-9]+ TRIPLET"
        h5group = joinpath(ensemble,rep,disc)
        writehdf5_spectrum_with_regexp(file,h5file,smearing_regex;mixed_rep=false,h5group=h5group,setup,filter_channels,channels,sort=true,deduplicate=true)
    end
end

filename = joinpath(output_dir, ensemble * "_spectrum.hdf5")
meson_metadata = CSV.read(meson_measurements_metadata, DataFrame)
ensemble_rows = filter(row -> row.ensemble_name == ensemble, meson_metadata)

for row in eachrow(ensemble_rows)

    ndisc_hits = row.nsrc
    rep = row.representation
    input_connected = row.conn_file_input
    input_disconnected = row.disc_file_input
    nconn_hits = 1
    
    conn_str = "CONN"
    disc_str = "DISC"

    # Write connected contributions
    main(filename; ensemble, rep, disc=conn_str, nhits=nconn_hits, file=input_connected, filter_channels=false, channels=nothing)
    
    # Write disconnected contributions
    main(filename; ensemble, rep, disc=disc_str, nhits=ndisc_hits, file=input_disconnected, filter_channels=false, channels=nothing)

end

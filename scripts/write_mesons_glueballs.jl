using Pkg; Pkg.activate("."); Pkg.instantiate()
using HiRepParsing
using HDF5
using DelimitedFiles

function main(h5file;ensemble,disc,nhits,file,setup=true,filter_channels=false,channels=nothing)
    isfile(h5file) && rm(h5file)
    if disc == "disc"
        smearing_regex = r"DISCON_SEMWALL smear_N[0-9]+ SINGLET"
        writehdf5_spectrum_disconnected_with_regexp(file,h5file,smearing_regex,nhits;mixed_rep=false,h5group=ensemble,setup,filter_channels,channels,sort=true,deduplicate=true)
    else
        smearing_regex = r"source_N[0-9]+_sink_N[0-9]+ TRIPLET"
        writehdf5_spectrum_with_regexp(file,h5file,smearing_regex;mixed_rep=false,h5group=ensemble,setup,filter_channels,channels,sort=true,deduplicate=true)
    end
end

for (ensemble,rep,disc,nhits,file) in eachrow(readdlm("input/listfile.txt",','))
    filename = ensemble * "_" * rep * "_" * disc * "_spectrum.hdf5"
    main(filename;ensemble,disc,nhits,file,filter_channels=false,channels=nothing)
end

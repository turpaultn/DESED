function demo_batchProcessing()

% This is an example script to process a whole dataset using the Audio
% Degradation Toolbox including code to translate given ground truth
% annotations.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Audio Degradation Toolbox
%
% Centre for Digital Music, Queen Mary University of London.
% This file copyright 2013 Sebastian Ewert, Matthias Mauch and QMUL.
%    
% This program is free software; you can redistribute it and/or
% modify it under the terms of the GNU General Public License as
% published by the Free Software Foundation; either version 2 of the
% License, or (at your option) any later version.  See the file
% COPYING included with this distribution for more information.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath(genpath(fullfile(pwd,'AudioDegradationToolbox')));

% the following file should list all the files to process. Every line
% should specify one audio file, one audio file and a ground truth file in
% CSV format, or just the ground truth file. This example scripts treats
% the first column of a CSV file as time information that needs to be
% adjusted. If this is not correct, the script needs to be adapted.

filename_listOfFiles = '../metadata/eval/soundscapes_generated_fbsnr/XdB.csv';
% read list of files to process
fid = fopen(filename_listOfFiles);
files=textscan(fid,'%s %s','delimiter',';');
fclose(fid);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1    testdata/472TNA3M_snippet.wav
% 2    testdata/clarinet.wav
% 3    testdata/p009m_drum.wav
% 4    testdata/RWC-C08.wav ; testdata/RWC-C08.csv
% 5    testdata/p009m_drum.csv
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% line 1-3: just process audio, line 4: process audio and ground truth data
% at the same time, line 5: process only ground truth data

% destination directory
outputDirectory = '../../segmented/eval/audio/soundscapes_final/distorted/';

% desired degradations
degradationnames = {'smartPhonePlayback', ...
                    'smartPhoneRecording', ...
                    'unit_applyClippingAlternative', ...
                    'unit_applyDynamicRangeCompression',...
                    'unit_applyHighpassFilter', ...
                    'unit_applyLowpassFilter'};
nDegradation = length(degradationnames);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

numLines = length(files{1});
if length(files)>1 && (length(files{2}) < numLines)
    files{2}{length(files{2})+1:numLines} = '';
end
files{1} = strtrim(files{1});
files{2} = strtrim(files{2});

% create outputDirectory if necessary
if ~exist(outputDirectory,'dir')
    mkdir(outputDirectory);
end

% loop over files to process
for k=1:numLines  % use this if you have the parallel computing toolbox
% for k=1:numLines
    [path1,name1,ext1] = fileparts(files{1}{k});
    [path2,name2,ext2] = fileparts(files{2}{k});
    
    % check whether a wav and/or csv file is given
    audiofilename = []; audiopath = []; csvfilename=[]; csvpath = [];
    if strcmpi(ext1,'.csv')
        csvpath = path1;
        csvfilename = [name1,ext1];
    elseif strcmpi(ext1,'.wav')
        audiopath = path1;
        audiofilename = [name1,ext1];
    end
    if strcmpi(ext2,'.csv')
        csvpath = path2;
        csvfilename = [name2,ext2];
    elseif strcmpi(ext2,'.wav')
        audiopath = path2;
        audiofilename = [name2,ext2];
    end
    
    % Read audio and CSV data
    f_audio = []; samplingFreq = []; nbits = [];
    timepositions_beforeDegr = []; remainingColumns = [];
    if ~isempty(audiofilename)
        fprintf('Reading %s\n',audiofilename);
        [f_audio,samplingFreq] = audioread(fullfile(audiopath,audiofilename));
    end
    if ~isempty(csvfilename)
        fprintf('Reading %s\n',csvfilename);
        
        fid = fopen(fullfile(csvpath,csvfilename));
        linestring = fgetl(fid);
        numberOfColumns = length(strfind(linestring,','))+1;
        fclose(fid);
        
        fid = fopen(fullfile(csvpath,csvfilename));
        data = textscan(fid,['%f' repmat('%s', 1, numberOfColumns-1) '%*[^\n]'], 'delimiter', ',', 'collectoutput', true);
        fclose(fid);
        
        timepositions_beforeDegr = data{1};
        remainingColumns = data{2};
    end
    
    % apply degradations
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    for iDegradation = 1:nDegradation
        degradationname = degradationnames{iDegradation};
        PathToOutput = fullfile(outputDirectory,degradationname);
        if ~exist(PathToOutput,'dir') mkdir(PathToOutput); end
        [f_audio_out,timepositions_afterDegr] = applyDegradation(degradationname, f_audio, samplingFreq, timepositions_beforeDegr);

        if ~isempty(audiofilename)
            audiowrite(fullfile(PathToOutput,audiofilename),f_audio_out,samplingFreq);
        end
        if ~isempty(csvfilename)
            writeCsvFile(fullfile(PathToOutput,csvfilename),timepositions_afterDegr,remainingColumns);
        end
    end
end

end



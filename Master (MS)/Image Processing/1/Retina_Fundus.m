%% Project 1 - Retina Fundus Preprocessing (All steps in one run)
% Course: Digital Image Processing
% Steps: Green channel -> Denoise -> Illumination correction (opening/subtract)
%        -> Contrast enhancement -> Edge-based enhancement -> Evaluation + Save
%
% Best methods are ACTIVE; alternatives are kept as COMMENTED options.

clear; close all; clc;

%% ----------------------- Settings -----------------------
inputDir  = pwd;
outputDir = fullfile(inputDir, 'Outputs');
if ~exist(outputDir, 'dir'), mkdir(outputDir); end

% Create stage subfolders
stages = {'01_green','02_denoise','03_illum_correct','04_contrast','05_edges','06_final','figures'};
for i = 1:numel(stages)
    d = fullfile(outputDir, stages{i});
    if ~exist(d, 'dir'), mkdir(d); end
end

% Find images (covers Im281_1 ... Im288_1 as requested)
files = dir(fullfile(inputDir, 'Im28*-1.tif'));
if isempty(files)
    error('No input images found. Put this script in the same folder as Im281_1.tif ... Im288_1.tif');
end

% Parameters (can be tuned if needed)
claheClipLimit = 0.01;         % good default for fundus
claheNumTiles  = [8 8];
edgeBoost      = 0.20;         % boost on edges (0..1)
edgeMethodBest = 'Canny';      % chosen best (alternatives commented)
saveAs = 'png';                % output format

%% ----------------------- Metrics Table -----------------------
% Metrics requested: Mean, Std, Contrast index, Edge pixel count (Sobel)
names      = strings(numel(files),1);
Mean_G     = zeros(numel(files),1);
Std_G      = zeros(numel(files),1);
Contr_G    = zeros(numel(files),1);
EdgeSobel  = zeros(numel(files),1);

Mean_Final = zeros(numel(files),1);
Std_Final  = zeros(numel(files),1);
Contr_Final= zeros(numel(files),1);
EdgeSobelF = zeros(numel(files),1);

%% ----------------------- Main Loop -----------------------
for k = 1:numel(files)
    fname = files(k).name;
    [~, base, ~] = fileparts(fname);
    names(k) = string(base);

    % ---------- Read ----------
    I = imread(fullfile(inputDir, fname));
    if ndims(I) == 3
        % Step 1: Green channel extraction (best for vessels contrast)
        G = I(:,:,2);
    else
        % If image already grayscale, treat it as "green"
        G = I;
    end
    Gd = im2double(G); % work in [0,1]

    % Save stage 01
    imwrite(Gd, fullfile(outputDir,'01_green', base + "_green." + saveAs));

    % ---------- Step 2: Noise removal ----------
    % BEST (ACTIVE): Non-Local Means filtering (usually very good for medical images)
    % Reason: preserves fine vessel structures better than simple smoothing.
    % Note: requires Image Processing Toolbox.
    % Automatic-ish smoothing based on image variability:
    deg = max(0.001, 0.6 * std2(Gd));  % heuristic
    Gden = imnlmfilt(Gd, 'DegreeOfSmoothing', deg);

    % --- Alternatives (COMMENTED) ---
    % Gden = medfilt2(Gd, [3 3]);                 % good for salt & pepper, may distort thin vessels
    % Gden = wiener2(Gd, [5 5]);                  % adaptive, can blur small structures
    % Gden = imgaussfilt(Gd, 1.0);                % simple but blurs vessels
    % Gden = imbilatfilt(Gd);                     % edge-preserving, may be slower / needs tuning

    imwrite(Gden, fullfile(outputDir,'02_denoise', base + "_denoise." + saveAs));

    % ---------- Step 3: Uneven illumination correction ----------
    % Use morphological opening to estimate background then subtract.
    % Structuring element size should be larger than vessel width.
    [H,W] = size(Gden);
    radius = round(0.04 * min(H,W)); % heuristic: 4% of min dimension
    radius = max(radius, 15);        % minimum safety
    se = strel('disk', radius);

    background = imopen(Gden, se);           % estimate illumination/background
    Icorr = imsubtract(Gden, background);    % subtract background
    Icorr = mat2gray(Icorr);                % normalize to [0,1]

    % --- Alternatives (COMMENTED) ---
    % background = imgaussfilt(Gden, 25);     % low-pass background estimate (not as robust as opening)
    % Icorr = mat2gray(Gden - background);

    imwrite(background, fullfile(outputDir,'03_illum_correct', base + "_background." + saveAs));
    imwrite(Icorr,      fullfile(outputDir,'03_illum_correct', base + "_illumcorr." + saveAs));

    % ---------- Step 4: Contrast enhancement ----------
    % BEST (ACTIVE): adapthisteq (CLAHE) for local contrast, highlights vessels/lesions
    Icon = adapthisteq(Icorr, 'ClipLimit', claheClipLimit, 'NumTiles', claheNumTiles);

    % --- Alternatives (COMMENTED) ---
    % Icon = imadjust(Icorr);                 % global, may be insufficient for local vessel contrast
    % Icon = histeq(Icorr);                   % can over-amplify noise / wash out regions

    imwrite(Icon, fullfile(outputDir,'04_contrast', base + "_contrast." + saveAs));

    % ---------- Step 5: Edge-based enhancement ----------
    % BEST (ACTIVE): Canny edges (good localization + noise robustness)
    edgeMask = edge(Icon, edgeMethodBest);

    % --- Alternatives (COMMENTED) ---
    % edgeMask = edge(Icon, 'Sobel');
    % edgeMask = edge(Icon, 'Prewitt');
    % edgeMask = edge(Icon, 'Roberts');
    % edgeMask = edge(Icon, 'log');           % Laplacian of Gaussian

    % Enhance by boosting intensities on detected edges, then slight sharpening
    Ifinal = Icon;
    Ifinal(edgeMask) = min(Ifinal(edgeMask) + edgeBoost, 1);

    % Optional additional sharpening (kept mild)
    Ifinal = imsharpen(Ifinal, 'Radius', 1.5, 'Amount', 0.8);

    imwrite(edgeMask, fullfile(outputDir,'05_edges', base + "_edges_" + edgeMethodBest + "." + saveAs));
    imwrite(Ifinal,   fullfile(outputDir,'06_final', base + "_final." + saveAs));

    % ---------- Step 6: Evaluation (quantitative) ----------
    % Define contrast index (ACTIVE): Michelson contrast
    % C = (max-min)/(max+min)
    % --- Alternatives (COMMENTED) ---
    % Contr = std2(I) / (mean2(I) + eps);     % coefficient of variation (RMS-like)
    % Contr = std2(I);                         % RMS contrast

    Mean_G(k)  = mean(Gd(:));
    Std_G(k)   = std(Gd(:));
    Contr_G(k) = (max(Gd(:)) - min(Gd(:))) / (max(Gd(:)) + min(Gd(:)) + eps);
    EdgeSobel(k)= nnz(edge(Gd, 'Sobel'));     % requested Sobel edge pixel count

    Mean_Final(k)   = mean(Ifinal(:));
    Std_Final(k)    = std(Ifinal(:));
    Contr_Final(k)  = (max(Ifinal(:)) - min(Ifinal(:))) / (max(Ifinal(:)) + min(Ifinal(:)) + eps);
    EdgeSobelF(k)   = nnz(edge(Ifinal, 'Sobel'));

    % ---------- Qualitative visualization (save figure) ----------
    fig = figure('Visible','off','Color','w','Position',[100 100 1400 700]);
    tiledlayout(2,4,'Padding','compact','TileSpacing','compact');

    nexttile; imshow(Gd,[]); title('Green Channel');
    nexttile; imshow(Gden,[]); title('Denoised');
    nexttile; imshow(background,[]); title('Estimated Background (Opening)');
    nexttile; imshow(Icorr,[]); title('Illumination Corrected');

    nexttile; imshow(Icon,[]); title('Contrast (CLAHE)');
    nexttile; imshow(edgeMask); title(['Edges: ' edgeMethodBest]);
    nexttile; imshow(Ifinal,[]); title('Final Enhanced');
    nexttile; imshowpair(Gd, Ifinal, 'montage'); title('Before | After');

    exportgraphics(fig, fullfile(outputDir,'figures', base + "_pipeline.png"), 'Resolution', 150);
    close(fig);
end

%% ----------------------- Save metrics table -----------------------
T = table(names, ...
    Mean_G, Std_G, Contr_G, EdgeSobel, ...
    Mean_Final, Std_Final, Contr_Final, EdgeSobelF, ...
    'VariableNames', {'Image','Mean_Green','Std_Green','ContrastIdx_Green','EdgePixels_Sobel_Green', ...
                      'Mean_Final','Std_Final','ContrastIdx_Final','EdgePixels_Sobel_Final'});

disp(T);

writetable(T, fullfile(outputDir, 'metrics.csv'));

% Also save as MAT for convenience
save(fullfile(outputDir, 'metrics.mat'), 'T');

%% ----------------------- Short analysis (printed) -----------------------
fprintf('\n=== Short Analysis (for report) ===\n');
fprintf('Noise removal: imnlmfilt chosen to reduce noise while preserving thin vessels.\n');
fprintf('Illumination correction: morphological opening estimates background illumination and subtracting it reduces non-uniform lighting.\n');
fprintf('Contrast: adapthisteq (CLAHE) chosen for local contrast enhancement, making vessels/lesions more visible.\n');
fprintf('Edge enhancement: Canny edges used and boosted slightly + mild sharpening for clearer vessel boundaries.\n');
fprintf('Outputs saved in: %s\n', outputDir);

%% CV Project 3 - Nucleomegaly Segmentation & Feature Extraction
% Author: <نام شما>
% Input: plasma.jpg  (same folder)
% Output: figures + CSV tables
% نیازمند Image Processing Toolbox

clear; close all; clc;

%% 1) Load image
Irgb = imread('plasma.jpg');

% برای تولید خروجی‌ها در یک پوشه
outDir = fullfile(pwd, 'outputs_project3');
if ~exist(outDir, 'dir'), mkdir(outDir); end

%% 1) Pre-processing: Choose best channel (AUTO) + grayscale
% ایده: چون هسته‌ها (nuclei) در این تصویر تیره‌تر هستند، با یک تست ساده‌ی Otsu
% روی هر کانال، میزان جدایش foreground/background را امتیازدهی می‌کنیم و بهترین کانال را انتخاب می‌کنیم.

chNames = {'R','G','B'};
scores  = zeros(1,3);

for k = 1:3
    Ik = im2double(Irgb(:,:,k));
    T  = graythresh(Ik);      % Otsu threshold
    bw = imbinarize(Ik, T);   % foreground=bright by default
    bw = ~bw;                 % چون هسته‌ها تیره‌اند، برعکس می‌کنیم
    
    fg = Ik(bw);  bg = Ik(~bw);
    scores(k) = abs(mean(fg) - mean(bg)) / (std(Ik(:)) + eps);
end

[~, bestIdx] = max(scores);
Igray = im2double(Irgb(:,:,bestIdx));
bestChannelName = chNames{bestIdx};

fprintf('Selected channel: %s (score=%.3f)\n', bestChannelName, scores(bestIdx));

% بهبود کنتراست (فعال)
Ieq = adapthisteq(Igray, 'ClipLimit', 0.02);

% ------------------ روش‌های جایگزین (غیرفعال با کامنت) ------------------
% Ieq = imadjust(Igray);                        % ساده‌تر از CLAHE
% Ieq = medfilt2(Igray, [3 3]);                 % کاهش نویز (ممکن است لبه‌ها را نرم کند)
% Ieq = imgaussfilt(Igray, 1);                  % فیلتر گاوسی
% ------------------------------------------------------------------------

%% 2) Segmentation (BEST ACTIVE): Black-hat + Otsu + Morphology + Watershed split
% چرا Black-hat (imbothat)؟
% چون هسته‌ها نسبتاً تیره‌اند؛ black-hat (closing - image) نواحی تیره را برجسته می‌کند
% و بعد آستانه‌گذاری تمیزتر می‌شود.

seR = 15;  % شعاع ساختار مورفولوژیک (قابل تنظیم)
Ibh = imbothat(Ieq, strel('disk', seR));   % هسته‌ها در Ibh روشن‌تر می‌شوند

% آستانه‌گذاری (فعال)
Tbh = graythresh(Ibh);
bw0 = imbinarize(Ibh, Tbh);

% پاکسازی مورفولوژیک (فعال)
minArea = 150;                      % حذف اجسام خیلی کوچک (نویز)
bw1 = bwareaopen(bw0, minArea);
bw1 = imclose(bw1, strel('disk', 2));
bw1 = imfill(bw1, 'holes');

% --- جداسازی سلول‌های چسبیده با Watershed (فعال) ---
D = bwdist(~bw1);
% مارکرها از بیشینه‌های فاصله (تقریباً مرکز هر هسته)
mx = imextendedmax(D, 2);          % ارتفاع 2 قابل تنظیم
mx = imclose(mx, strel('disk', 1));
mx = bwareaopen(mx, 20);
D2 = imimposemin(-D, mx);
Lw = watershed(D2);

bwFinal = bw1;
bwFinal(Lw == 0) = 0;              % مرزهای watershed حذف شوند

% ------------------ روش‌های جایگزین Segmentation (غیرفعال) ------------------
% % (A) فقط Otsu روی تصویر معکوس (سریع ولی معمولاً ضعیف‌تر)
% T = graythresh(Ieq);
% bw0 = ~imbinarize(Ieq, T);
%
% % (B) Adaptive threshold (وقتی روشنایی غیر یکنواخت باشد)
% bw0 = imbinarize(Ieq, 'adaptive', 'ForegroundPolarity','dark', 'Sensitivity',0.48);
%
% % (C) HSV/Color-based (گاهی خوب است ولی وابسته به رنگ‌آمیزی)
% Ihsv = rgb2hsv(Irgb);
% S = Ihsv(:,:,2); V = Ihsv(:,:,3);
% bw0 = S > 0.35 & V < 0.85;
% bw0 = bwareaopen(bw0, 150);
% ---------------------------------------------------------------------------

%% 3) Labeling & Feature Extraction
L = bwlabel(bwFinal);
stats = regionprops(L, Igray, 'Area','Eccentricity','PixelIdxList','Centroid');

n = numel(stats);
Area = zeros(n,1);
Ecc  = zeros(n,1);
StdIntensity = zeros(n,1);

for i = 1:n
    Area(i) = stats(i).Area;
    Ecc(i)  = stats(i).Eccentricity;

    pix = Igray(stats(i).PixelIdxList);
    StdIntensity(i) = std(pix); % انحراف معیار شدت خاکستری داخل سلول/هسته
end

%% 4) Simple Nucleomegaly Heuristic (Healthy vs Suspicious)
% چون برچسب واقعی نداریم، یک معیار ساده: بزرگ‌ترین هسته‌ها را "مشکوک" در نظر می‌گیریم.
% اینجا از صدک 85% استفاده می‌کنیم (قابل تغییر).
p = 85;
thrArea = prctile(Area, p);
isSuspicious = Area >= thrArea;

%% 4) Statistical summary (mean ± std) for each group
groupNames = ["All"; "Healthy"; "Suspicious"];
A_mean = [mean(Area); mean(Area(~isSuspicious)); mean(Area(isSuspicious))];
A_std  = [std(Area);  std(Area(~isSuspicious));  std(Area(isSuspicious))];

E_mean = [mean(Ecc); mean(Ecc(~isSuspicious)); mean(Ecc(isSuspicious))];
E_std  = [std(Ecc);  std(Ecc(~isSuspicious));  std(Ecc(isSuspicious))];

S_mean = [mean(StdIntensity); mean(StdIntensity(~isSuspicious)); mean(StdIntensity(isSuspicious))];
S_std  = [std(StdIntensity);  std(StdIntensity(~isSuspicious));  std(StdIntensity(isSuspicious))];

summaryTbl = table(groupNames, A_mean, A_std, E_mean, E_std, S_mean, S_std, ...
    'VariableNames', {'Group','AreaMean','AreaStd','EccMean','EccStd','StdIntMean','StdIntStd'});

disp(summaryTbl);

%% Save feature tables
id = (1:n).';
featuresTbl = table(id, Area, Ecc, StdIntensity, isSuspicious, ...
    'VariableNames', {'ID','Area','Eccentricity','StdIntensity','Suspicious'});
writetable(featuresTbl, fullfile(outDir, 'cell_features.csv'));
writetable(summaryTbl,  fullfile(outDir, 'feature_summary.csv'));

%% 5) Visualization
% 5-1: original + chosen channel + black-hat + threshold mask
f1 = figure('Name','Step-by-step', 'Color','w');
tiledlayout(2,2, 'Padding','compact', 'TileSpacing','compact');

nexttile; imshow(Irgb); title('Original (RGB)');
nexttile; imshow(Igray, []); title(['Selected Channel (', bestChannelName, ')']);
nexttile; imshow(Ibh, []); title('Black-hat (imbothat) result');
nexttile; imshow(bw0); title('Threshold mask (before morph)');

exportgraphics(f1, fullfile(outDir,'01_steps.png'), 'Resolution',200);

% 5-2: morphology result + final mask
f2 = figure('Name','Morphology', 'Color','w');
tiledlayout(1,2, 'Padding','compact', 'TileSpacing','compact');
nexttile; imshow(bw1); title('After Morphology (clean + fill)');
nexttile; imshow(bwFinal); title('Final mask (after Watershed split)');
exportgraphics(f2, fullfile(outDir,'02_morph.png'), 'Resolution',200);

% 5-3: Final boundaries with healthy vs suspicious (green vs red)
B = bwboundaries(bwFinal);
f3 = figure('Name','Final boundaries', 'Color','w');
imshow(Irgb); hold on;
hHealthy = plot(nan,nan,'g','LineWidth',1.0);
hSusp    = plot(nan,nan,'r','LineWidth',1.5);

for k = 1:numel(B)
    b = B{k};
    % label from first boundary pixel
    lab = L(b(1,1), b(1,2));
    if lab == 0, continue; end

    if isSuspicious(lab)
        plot(b(:,2), b(:,1), 'r', 'LineWidth',1.5);
    else
        plot(b(:,2), b(:,1), 'g', 'LineWidth',1.0);
    end
end

legend([hHealthy, hSusp], {'Healthy','Suspicious (by area)'}, 'TextColor','k');
title(sprintf('Final detection | Suspicious: Area >= prctile(Area,%d)=%.1f | n=%d', p, thrArea, n));
hold off;
exportgraphics(f3, fullfile(outDir,'03_final_boundaries.png'), 'Resolution',220);

% 5-4: Statistical plots (Histogram + Boxplot)
f4 = figure('Name','Statistics', 'Color','w');
tiledlayout(2,3, 'Padding','compact', 'TileSpacing','compact');

nexttile; histogram(Area); title('Area - Histogram'); xlabel('Area (px)'); ylabel('Count');
nexttile; histogram(Ecc);  title('Eccentricity - Histogram'); xlabel('Ecc'); ylabel('Count');
nexttile; histogram(StdIntensity); title('Std(Intensity) - Histogram'); xlabel('Std'); ylabel('Count');

%nexttile; boxplot(Area, isSuspicious, 'Labels',{'Healthy','Suspicious'}); title('Area - Boxplot');
%nexttile; boxplot(Ecc,  isSuspicious, 'Labels',{'Healthy','Suspicious'}); title('Eccentricity - Boxplot');
%nexttile; boxplot(StdIntensity, isSuspicious, 'Labels',{'Healthy','Suspicious'}); title('Std(Intensity) - Boxplot');

exportgraphics(f4, fullfile(outDir,'04_statistics.png'), 'Resolution',220);

fprintf('\nDone. Outputs saved to: %s\n', outDir);

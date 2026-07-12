%% CV_Project2_RANSAC_SURF.m
% پروژه 2: تشخیص شیء با ویژگی‌های محلی + RANSAC (Affine)
% خروجی‌ها:
% 1) تطبیق ویژگی قبل از RANSAC
% 2) تطبیق ویژگی بعد از RANSAC
% 3) تصویر نهایی همراه با ترسیم محدوده شیء تشخیص داده شده
%
% نویسنده: (نام خودتان)
% تاریخ: (تاریخ)

clear; close all; clc;

%% ---------- تنظیمات ----------
targetFile = 'Target.png';
sceneFile  = 'Traffic.jpg';

% --- مسیر پوشه‌ی خروجی را کنار خودِ فایل .m بساز ---
scriptFullPath = mfilename('fullpath');
if isempty(scriptFullPath)
    % اگر Live Script یا حالت‌هایی که mfilename خالی است
    scriptDir = pwd;
else
    scriptDir = fileparts(scriptFullPath);
end

outDir = fullfile(scriptDir, 'outputs');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

% پارامترهای SURF
metricThresholdTarget = 500;   % اگر کم/زیاد بود قابل تنظیم است
metricThresholdScene  = 500;
numStrongest          = 800;   % تعداد نقاط کلیدی (برای سرعت/کیفیت قابل تنظیم)

% پارامترهای تطبیق
maxRatio       = 0.75;         % Lowe ratio-like filtering
matchThreshold = 40;           % سخت‌گیری تطبیق (کمتر => سخت‌گیرتر)

% پارامترهای RANSAC
maxDistance  = 3.0;            % آستانه خطای بازفرافکنی (pixels)
maxNumTrials = 4000;
confidence   = 99.9;

%% ---------- 0) خواندن تصاویر ----------
assert(exist(targetFile,'file')==2, 'فایل %s پیدا نشد.', targetFile);
assert(exist(sceneFile,'file')==2,  'فایل %s پیدا نشد.', sceneFile);

I_target = imread(targetFile);
I_scene  = imread(sceneFile);

if size(I_target,3) == 3, I_target_gray = rgb2gray(I_target); else, I_target_gray = I_target; end
if size(I_scene,3)  == 3, I_scene_gray  = rgb2gray(I_scene);  else, I_scene_gray  = I_scene;  end

%% ---------- 1) استخراج نقاط کلیدی SURF ----------
ptsTarget = detectSURFFeatures(I_target_gray, 'MetricThreshold', metricThresholdTarget);
ptsScene  = detectSURFFeatures(I_scene_gray,  'MetricThreshold', metricThresholdScene);

ptsTarget = ptsTarget.selectStrongest(numStrongest);
ptsScene  = ptsScene.selectStrongest(numStrongest);

%% ---------- 2) استخراج توصیفگرها ----------
% upright=false یعنی نسبت به چرخش هم مقاوم‌تر
[featTarget, validTarget] = extractFeatures(I_target_gray, ptsTarget, 'Upright', false);
[featScene,  validScene]  = extractFeatures(I_scene_gray,  ptsScene,  'Upright', false);

%% ---------- 3) تطبیق ویژگی‌ها (قبل از RANSAC) ----------
indexPairs = matchFeatures(featTarget, featScene, ...
    'Unique', true, ...
    'MaxRatio', maxRatio, ...
    'MatchThreshold', matchThreshold);

matchedTarget = validTarget(indexPairs(:,1));
matchedScene  = validScene(indexPairs(:,2));

fprintf('تعداد تطبیق‌های اولیه (قبل از RANSAC): %d\n', matchedTarget.Count);

% نمایش تطبیق قبل از RANSAC
fig1 = figure('Name','Matches BEFORE RANSAC','Color','w');
showMatchedFeatures(I_target, I_scene, matchedTarget, matchedScene, 'montage');
title(sprintf('Feature Matches BEFORE RANSAC (N = %d)', matchedTarget.Count));
drawnow;
exportgraphics(fig1, fullfile(outDir, 'matches_before_RANSAC.png'), 'Resolution', 200);

%% ---------- 4) حذف تطبیق‌های نادرست با RANSAC (Affine) ----------
% تخمین تبدیل از Target به Scene
% estimateGeometricTransform2D: ورودی‌ها (movingPoints, fixedPoints)
% moving = نقاط در Target ، fixed = نقاط در Scene
[tform, inlierIdx] = estimateGeometricTransform2D( ...
    matchedTarget, matchedScene, 'affine', ...
    'MaxDistance',  maxDistance, ...
    'MaxNumTrials', maxNumTrials, ...
    'Confidence',   confidence);

inlierTarget = matchedTarget(inlierIdx);
inlierScene  = matchedScene(inlierIdx);

fprintf('تعداد inlier بعد از RANSAC: %d\n', inlierTarget.Count);
fprintf('نسبت inlier: %.2f%%\n', 100 * inlierTarget.Count / max(matchedTarget.Count,1));

% نمایش تطبیق بعد از RANSAC (فقط inlierها)
fig2 = figure('Name','Matches AFTER RANSAC','Color','w');
showMatchedFeatures(I_target, I_scene, inlierTarget, inlierScene, 'montage');
title(sprintf('Feature Matches AFTER RANSAC (Inliers = %d / %d)', ...
    inlierTarget.Count, matchedTarget.Count));
drawnow;
exportgraphics(fig2, fullfile(outDir, 'matches_after_RANSAC.png'), 'Resolution', 200);

%% ---------- 5) تشخیص نهایی شیء و رسم چهارضلعی محدوده ----------
% گوشه‌های تصویر Target (مرز مستطیلی آن)
[hT, wT, ~] = size(I_target);
targetBox = [ ...
    1,   1; ...
    wT,  1; ...
    wT, hT; ...
    1,  hT; ...
    1,   1  ];

% انتقال گوشه‌ها به مختصات Scene با تبدیل تخمین‌زده‌شده
sceneBox = transformPointsForward(tform, targetBox);

fig3 = figure('Name','Detected Object','Color','w');
imshow(I_scene); hold on;
plot(sceneBox(:,1), sceneBox(:,2), 'g-', 'LineWidth', 3);
title('Detected Target in Scene (Affine + RANSAC)');
hold off;
drawnow;
exportgraphics(fig3, fullfile(outDir, 'detected_object_polygon.png'), 'Resolution', 200);

%% ---------- ذخیره خلاصه متنی ----------
summaryFile = fullfile(outDir, 'run_summary.txt');
fid = fopen(summaryFile, 'w');
fprintf(fid, 'Initial matches (before RANSAC): %d\n', matchedTarget.Count);
fprintf(fid, 'Inliers (after RANSAC): %d\n', inlierTarget.Count);
fprintf(fid, 'Inlier ratio: %.2f%%\n', 100 * inlierTarget.Count / max(matchedTarget.Count,1));
fprintf(fid, 'RANSAC params: MaxDistance=%.2f, MaxNumTrials=%d, Confidence=%.1f\n', ...
    maxDistance, maxNumTrials, confidence);
fclose(fid);

disp('تمام خروجی‌ها در پوشه outputs ذخیره شدند:');
disp('- matches_before_RANSAC.png');
disp('- matches_after_RANSAC.png');
disp('- detected_object_polygon.png');
disp('- run_summary.txt');

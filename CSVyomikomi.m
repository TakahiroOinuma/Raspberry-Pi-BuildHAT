% CSVファイルを3つ読み込む
fileNames = {'lognobarria.csv', 'loglinear.csv', 'logsigumo.csv'};
dataList = cell(1, length(fileNames));

for i = 1:length(fileNames)
    dataList{i} = readtable(fileNames{i});
end

% ステップ数を時間軸として設定
graphsPerFile = 3; % 1ファイルあたりのグラフ数
numStepsList = cellfun(@height, dataList); % 各ファイルのステップ数

% 各ファイルのプロットを設定
figure;
for i = 1:length(fileNames)
    data = dataList{i};
    Time = (1:numStepsList(i))'; % ステップごとのインデックスを時間軸にする

    % Joy_LYとLeft_Speedをプロット
    subplot(length(fileNames), graphsPerFile, (i-1)*graphsPerFile+1); % ファイルごとの1番目のプロット
    hold on;
    plot(Time, data.Joy_LY, 'DisplayName', 'Joy LY');
    plot(Time, data.Left_Speed, 'DisplayName', 'Left Speed');
    title(sprintf('Joystick Input and Motor Output (Left) - %d', i), 'FontSize', 14);
    xlabel('Step', 'FontSize', 12);
    ylabel('Values', 'FontSize', 12);
    ylim([-110 110]);
    legend('show');
    box on;
    hold off;

    % Joy_RYとRight_Speedをプロット
    subplot(length(fileNames), graphsPerFile, (i-1)*graphsPerFile+2); % ファイルごとの2番目のプロット
    hold on;
    plot(Time, data.Joy_RY, 'DisplayName', 'Joy RY');
    plot(Time, data.Right_Speed, 'DisplayName', 'Right Speed');
    title(sprintf('Joystick Input and Motor Output (Right) -  %d', i), 'FontSize', 14);
    xlabel('Step', 'FontSize', 12);
    ylabel('Values', 'FontSize', 12);
    ylim([-110 110]);
    legend('show');
    box on;
    hold off;

    % 距離センサーの値（Distance）をプロット
    subplot(length(fileNames), graphsPerFile, (i-1)*graphsPerFile+3); % ファイルごとの3番目のプロット
    plot(Time, data.Distance, 'DisplayName', 'Distance');
    title(sprintf('Distance Sensor -  %d', i), 'FontSize', 14);
    xlabel('Step', 'FontSize', 12);
    ylabel('Distance (m)', 'FontSize', 12);
    ylim([-0.1 2]);
    box on;
    legend('show');
end

% 必要に応じてグラフを画像として保存
% saveas(gcf, 'output_plot.png');

u_values = [100, 50]; % 定数入力値のリスト
k1 = 6; % 線形パラメータ
h1 = 0.5; % 線形バリア距離
k2 = 20; % シグモイドパラメータ
h2 = 0.6; % シグモイドバリア距離
k3 = 6; %　logパラメータ1
h3 = 10;% logバリア距離

d = linspace(1, 0.1, 100); % 壁までの距離を1mから0.1mの範囲で変化

% グラフのプロット
figure;
hold on;

for u = u_values
    % 線形型制御バリア関数
    uh_linear = (u * 0.01 + k1 * (d - h1)) * 100;
    uh_linear = max(0, min(u, uh_linear)); % 制約を適用（uhがuを超えないようにする）
    uh_linear = max(0, min(u, uh_linear)); % 制約を適用（uhがuを超えないようにする）

    % シグモイド関数型
    uh_sigmoid = u ./ (1 + exp(-k2 * (d - h2)));
    % 制約を適用しない（シグモイドは自然に範囲内に収まる）

    % バリア関数非搭載型
    uh_no_barrier = u * ones(size(d));
    uh_no_barrier = max(0, min(u, uh_no_barrier)); % 制約を適用（uhがuを超えないようにする）

    % log型
    %uh_log = u+k*(2*t/(d-h3+k3)^ +((-2)*t(d-h3))/(1+(d-h3+k3 )^2 ));

    % プロット
    plot(d, uh_linear, 'LineWidth', 2.5, 'DisplayName', sprintf('Linear (u=%d)', u));
    plot(d, uh_sigmoid, '--', 'LineWidth', 2.5, 'DisplayName', sprintf('Sigmoid (u=%d)', u));
    plot(d, uh_no_barrier, ':', 'LineWidth', 2.5, 'DisplayName', sprintf('No Barrier (u=%d)', u));
    %plot(d, uh_log, '*', 'LineWidth', 2.5, 'DisplayName', sprintf('Log (u=%d)', u));
end

hold off;

% グラフの設定
grid on;
xlabel('Distance to Wall d (m)', 'FontSize', 30); % x軸ラベルを強調
ylabel('Output u_h', 'FontSize', 30); % y軸ラベルを強調
%title('Comparison of Control Barrier Functions with Constraints', 'FontSize', 16); % タイトルを強調
legend('show', 'FontSize', 30); % 凡例を大きく設定
set(gca, 'FontSize', 30); % 軸のフォントサイズを設定
set(gcf,'Color','w'); % 図全体の背景色を白に設定

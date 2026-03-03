rng('shuffle');  % 用当前时间做种子，每次运行顺序不同

blocks = [];
for b = 1:25
    blocks = [blocks; randperm(8)'];
end
% blocks 是 200x1，第 i 个 trial 的 odor_id = blocks(i)

% ----- 文件 1：纯数字（两列 trial_index, odor_id）-----
trial_index = (1:200)';
T = table(trial_index, blocks, 'VariableNames', {'trial_index', 'odor_id'});
writetable(T, 'odor_sequence_numbers.csv', 'WriteVariableNames', false);

% ----- 文件 2：it == k ? "D1:X" : ... "D1:0" -----
fid = fopen('odor_sequence_D1_format.txt', 'w');
for i = 1:200
    fprintf(fid, 'it == %d  ? "D1:%d" :\n', i, blocks(i));
end
fprintf(fid, '"D1:0"\n');
fclose(fid);

disp('Done. Saved: odor_sequence_numbers.csv and odor_sequence_D1_format.txt');
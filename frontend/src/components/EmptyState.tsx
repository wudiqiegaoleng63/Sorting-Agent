export default function EmptyState() {
  return (
    <div className="empty-state">
      <h2>开始使用 Excel Agent</h2>
      <p>上传一个 Excel 文件，然后输入任务，例如：</p>
      <ul>
        <li>查看这个 Excel 有哪些 sheet，并预览前几行</li>
        <li>按销售额降序排序，并导出结果文件</li>
        <li>按地区统计销售额，生成汇总表</li>
        <li>清理空行和重复数据</li>
      </ul>
    </div>
  );
}

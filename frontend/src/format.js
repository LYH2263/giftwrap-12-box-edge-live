// 三边尺寸统一标注：固定两位小数、统一分隔符「 × 」与单位 m。
// 清单摘要、详情摘要、算纸下拉标注共用，保证三处同源同形。
export const fmtDim = (v) => Number(v).toFixed(2)
export const fmtDims = (l, w, h) => `${fmtDim(l)} × ${fmtDim(w)} × ${fmtDim(h)} m`

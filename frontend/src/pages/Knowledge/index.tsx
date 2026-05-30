import React, { useState, useEffect } from 'react';
import { 
  Row, Col, Card, List, Input, Tag, Tabs, Typography, Badge, 
  Space, Button, Skeleton, Empty, Divider, Breadcrumb, message,
  Statistic, Timeline, Progress, Descriptions, Modal, Rate
} from 'antd';
import {
  BookOutlined,
  SearchOutlined,
  EyeOutlined,
  LikeOutlined,
  ClockCircleOutlined,
  TagOutlined,
  FilterOutlined,
  ThunderboltOutlined,
  MedicineBoxOutlined,
  ExperimentOutlined,
  ReadOutlined,
  CalendarOutlined,
  BulbOutlined,
  HomeOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';
import './index.css';

const { Title, Paragraph, Text } = Typography;

const MotionCard = motion(Card);

const KnowledgeBase = () => {
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  
  // 知识分类数据
  const categories = [
    { id: 1, name: 'BI-RADS 标准', code: 'birads', icon: 'radiology', articleCount: 2, color: '#667eea' },
    { id: 2, name: '中医证型', code: 'zheng-type', icon: 'traditional-medicine', articleCount: 1, color: '#f093fb' },
    { id: 3, name: '治疗方案', code: 'treatment', articleCount: 1, color: '#f5576c' },
    { id: 4, name: '影像特征', code: 'ultrasound', articleCount: 1, color: '#4facfe' },
    { id: 5, name: '病理知识', code: 'pathology', articleCount: 1, color: '#10b981' },
    { id: 6, name: '随访管理', code: 'followup', articleCount: 1, color: '#f59e0b' },
    { id: 7, name: 'AI 模型', code: 'ai-model', articleCount: 1, color: '#8b5cf6' },
  ];
  
  // 文章列表
  const articles = [
    {
      id: 1,
      title: 'BI-RADS 分类标准详解',
      summary: '详细解读 BI-RADS 0-6 类分类标准及超声特征，涵盖各级别的定义、恶性风险、处理建议和随访周期。',
      categoryId: 1,
      categoryName: 'BI-RADS 标准',
      viewCount: 1256,
      likeCount: 89,
      tags: ['诊断标准', 'BI-RADS'],
      createdAt: '2026-05-20',
      readTime: '15 min'
    },
    {
      id: 2,
      title: '乳腺超声 BI-RADS 词典',
      summary: '乳腺超声 BI-RADS 标准化术语词典，包含肿块定义、特征描述规范及相关征象评估标准。',
      categoryId: 1,
      categoryName: 'BI-RADS 标准',
      viewCount: 982,
      likeCount: 67,
      tags: ['影像学', 'BI-RADS'],
      createdAt: '2026-05-22',
      readTime: '12 min'
    },
    {
      id: 3,
      title: '中医体质辨识与乳腺疾病',
      summary: '中医 9 种体质与乳腺疾病易感性及相关诊疗方案，涵盖体质特征、调理原则及常用方剂。',
      categoryId: 2,
      categoryName: '中医证型',
      viewCount: 1534,
      likeCount: 142,
      tags: ['中医诊疗', '诊断标准'],
      createdAt: '2026-05-18',
      readTime: '18 min'
    },
    {
      id: 4,
      title: '乳腺癌综合治疗方案',
      summary: '乳腺癌手术/放化疗/内分泌/靶向/免疫治疗综合方案，涵盖各治疗方式的适应症与疗效评估。',
      categoryId: 3,
      categoryName: '治疗方案',
      viewCount: 2341,
      likeCount: 198,
      tags: ['治疗指南', '分子分型'],
      createdAt: '2026-05-15',
      readTime: '25 min'
    },
    {
      id: 5,
      title: '乳腺超声影像特征分析',
      summary: '乳腺良恶性病变的超声影像特征及鉴别诊断，包含 AI 辅助诊断价值分析。',
      categoryId: 4,
      categoryName: '影像特征',
      viewCount: 1876,
      likeCount: 156,
      tags: ['影像学', 'AI 辅助'],
      createdAt: '2026-05-19',
      readTime: '20 min'
    },
    {
      id: 6,
      title: '乳腺癌病理分型与分子标志物',
      summary: '乳腺癌组织学分型、分子分型及免疫组化标志物解读，指导个体化治疗。',
      categoryId: 5,
      categoryName: '病理知识',
      viewCount: 1654,
      likeCount: 134,
      tags: ['病理学', '分子分型'],
      createdAt: '2026-05-17',
      readTime: '22 min'
    },
    {
      id: 7,
      title: '乳腺癌术后随访管理规范',
      summary: '乳腺癌术后规范化随访流程与监测重点，包含 AI 辅助随访管理。',
      categoryId: 6,
      categoryName: '随访管理',
      viewCount: 1432,
      likeCount: 121,
      tags: ['随访计划', 'AI 辅助'],
      createdAt: '2026-05-21',
      readTime: '16 min'
    },
    {
      id: 8,
      title: 'PBS-Net 软监督病灶分割模型',
      summary: 'PBS-Net 软监督病灶分割模型的技术原理与临床性能，权重来源：2,500 例本院超声图像自研训练，Dice 系数达 0.87。',
      categoryId: 7,
      categoryName: 'AI 模型',
      viewCount: 892,
      likeCount: 78,
      tags: ['AI 辅助', '诊断标准', '权重来源'],
      createdAt: '2026-05-24',
      readTime: '14 min'
    },
    {
      id: 9,
      title: '中医证型识别模型权重说明',
      summary: '中医体质辨识/证型识别/方剂推荐三个模型的权重来源，5,000 例三甲医院数据自研训练，准确率 0.89。',
      categoryId: 2,
      categoryName: '中医证型',
      viewCount: 567,
      likeCount: 45,
      tags: ['中医诊疗', 'AI 辅助', '权重来源'],
      createdAt: '2026-05-27',
      readTime: '16 min'
    },
  ];
  
  // 热门标签
  const hotTags = [
    { name: 'BI-RADS', count: 3, color: '#f59e0b' },
    { name: 'AI 辅助', count: 4, color: '#8b5cf6' },
    { name: '诊断标准', count: 3, color: '#667eea' },
    { name: '治疗指南', count: 2, color: '#f093fb' },
    { name: '影像学', count: 2, color: '#4facfe' },
    { name: '分子分型', count: 2, color: '#06b6d4' },
  ];
  
  // 分类统计图
  const categoryOption: EChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}篇',
    },
    series: [
      {
        name: '文章数量',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        data: categories.map((cat, i) => ({
          value: cat.articleCount,
          name: cat.name,
          itemStyle: { color: cat.color }
        })),
        label: {
          show: true,
          formatter: '{b}\n{c}篇'
        }
      },
    ],
  };
  
  // 阅读量趋势图
  const viewTrendOption: EChartOption = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: ['5/15', '5/16', '5/17', '5/18', '5/19', '5/20', '5/21', '5/22', '5/23', '5/24'],
    },
    yAxis: {
      type: 'value',
      name: '阅读量',
    },
    series: [
      {
        data: [2341, 2156, 1987, 1876, 1765, 1654, 1543, 1432, 1256, 1100],
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new (require('echarts')).graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' },
          ]),
        },
        itemStyle: {
          color: '#667eea',
        },
      },
    ],
  };
  
  return (
    <div className="knowledge-container">
      {/* 顶部统计 */}
      <Row gutter={[20, 20]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MotionCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Statistic
              title="知识文章"
              value={8}
              suffix="篇"
              valueStyle={{ color: '#667eea' }}
              prefix={<BookOutlined />}
            />
          </MotionCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MotionCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Statistic
              title="总阅读量"
              value={12837}
              suffix="次"
              valueStyle={{ color: '#f093fb' }}
              prefix={<EyeOutlined />}
            />
          </MotionCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MotionCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Statistic
              title="热门标签"
              value={10}
              suffix="个"
              valueStyle={{ color: '#10b981' }}
              prefix={<TagOutlined />}
            />
          </MotionCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MotionCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Statistic
              title="更新频率"
              value={5}
              suffix="篇/周"
              valueStyle={{ color: '#f59e0b' }}
              prefix={<ClockCircleOutlined />}
            />
          </MotionCard>
        </Col>
      </Row>
      
      {/* 主要内容区 */}
      <Row gutter={[20, 20]}>
        {/* 左侧文章列表 */}
        <Col xs={24} lg={16}>
          <MotionCard
            title={
              <Space>
                <BookOutlined style={{ color: '#667eea' }} />
                <span>知识库</span>
              </Space>
            }
            extra={
              <Input
                placeholder="搜索知识文章"
                prefix={<SearchOutlined />}
                style={{ width: 200 }}
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
              />
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* 分类标签 */}
            <Space wrap style={{ marginBottom: 16 }}>
              <Tag
                color={!selectedCategory ? '#667eea' : undefined}
                onClick={() => setSelectedCategory(null)}
                style={{ cursor: 'pointer', padding: '4px 12px' }}
              >
                全部
              </Tag>
              {categories.map((cat) => (
                <Tag
                  key={cat.id}
                  color={selectedCategory === cat.id ? cat.color : undefined}
                  onClick={() => setSelectedCategory(cat.id)}
                  style={{ cursor: 'pointer', padding: '4px 12px' }}
                >
                  {cat.name}
                </Tag>
              ))}
            </Space>
            
            <Divider style={{ margin: '12px 0' }} />
            
            {/* 文章列表 */}
            <List
              itemLayout="vertical"
              loading={loading}
              dataSource={articles.filter(art => 
                !selectedCategory || art.categoryId === selectedCategory
              ).filter(art =>
                !searchKeyword || 
                art.title.toLowerCase().includes(searchKeyword.toLowerCase()) ||
                art.summary.toLowerCase().includes(searchKeyword.toLowerCase())
              )}
              renderItem={(article) => (
                <List.Item
                  key={article.id}
                  extra={
                    <Space>
                      <Tag color="blue">{article.categoryName}</Tag>
                      {article.tags.map(tag => (
                        <Tag key={tag} color="default">{tag}</Tag>
                      ))}
                    </Space>
                  }
                >
                  <List.Item.Meta
                    title={
                      <Title level={4} style={{ marginBottom: 8 }}>
                        <a href={`#/knowledge/${article.id}`}>{article.title}</a>
                      </Title>
                    }
                    description={
                      <Paragraph ellipsis={{ rows: 2 }} style={{ color: '#666' }}>
                        {article.summary}
                      </Paragraph>
                    }
                  />
                  <Space split={<Divider type="vertical" />} style={{ marginTop: 12 }}>
                    <Text type="secondary">
                      <EyeOutlined /> {article.viewCount} 阅读
                    </Text>
                    <Text type="secondary">
                      <LikeOutlined /> {article.likeCount} 点赞
                    </Text>
                    <Text type="secondary">
                      <ClockCircleOutlined /> {article.readTime}
                    </Text>
                  </Space>
                </List.Item>
              )}
              locale={{ emptyText: '暂无文章' }}
            />
          </MotionCard>
        </Col>
        
        {/* 右侧边栏 */}
        <Col xs={24} lg={8}>
          {/* 分类统计 */}
          <MotionCard
            title={
              <Space>
                <FilterOutlined style={{ color: '#f093fb' }} />
                <span>分类统计</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            style={{ marginBottom: 20 }}
          >
            <ReactECharts option={categoryOption} style={{ height: 300 }} />
          </MotionCard>
          
          {/* 热门标签 */}
          <MotionCard
            title={
              <Space>
                <TagOutlined style={{ color: '#10b981' }} />
                <span>热门标签</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            style={{ marginBottom: 20 }}
          >
            <Space wrap>
              {hotTags.map((tag) => (
                <Tag
                  key={tag.name}
                  color={tag.color}
                  style={{ padding: '6px 12px', fontSize: 14 }}
                >
                  {tag.name} ({tag.count})
                </Tag>
              ))}
            </Space>
          </MotionCard>
          
          {/* 阅读量趋势 */}
          <MotionCard
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#667eea' }} />
                <span>阅读趋势</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <ReactECharts option={viewTrendOption} style={{ height: 200 }} />
          </MotionCard>
        </Col>
      </Row>
    </div>
  );
};

export default KnowledgeBase;

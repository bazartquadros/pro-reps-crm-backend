from src.models.user import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # vendas, clientes, leads, financeiro, performance
    description = db.Column(db.Text)
    generated_by = db.Column(db.String(100), nullable=False)  # Usuário que gerou
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    data = db.Column(db.JSON)  # Dados do relatório em formato JSON
    status = db.Column(db.String(20), nullable=False, default='Gerado')  # Gerado, Processando, Erro
    file_path = db.Column(db.String(300))  # Caminho do arquivo gerado (PDF, Excel, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'description': self.description,
            'generatedBy': self.generated_by,
            'periodStart': self.period_start.isoformat() if self.period_start else None,
            'periodEnd': self.period_end.isoformat() if self.period_end else None,
            'data': self.data,
            'status': self.status,
            'filePath': self.file_path,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_default_reports():
        """Cria relatórios padrão se não existirem"""
        if Report.query.count() == 0:
            reports = [
                Report(
                    title='Relatório de Vendas - Setembro 2024',
                    type='vendas',
                    description='Relatório mensal de vendas com análise de performance e metas atingidas.',
                    generated_by='Carlos Mendes',
                    period_start=datetime(2024, 9, 1),
                    period_end=datetime(2024, 9, 30),
                    data={
                        'total_vendas': 48500.00,
                        'numero_vendas': 3,
                        'ticket_medio': 16166.67,
                        'meta_mensal': 50000.00,
                        'percentual_meta': 97.0,
                        'vendas_por_representante': {
                            'Carlos Mendes': 40000.00,
                            'Ana Silva': 8500.00
                        }
                    },
                    status='Gerado'
                ),
                Report(
                    title='Análise de Clientes - 3º Trimestre 2024',
                    type='clientes',
                    description='Análise do comportamento e perfil dos clientes no terceiro trimestre.',
                    generated_by='Ana Silva',
                    period_start=datetime(2024, 7, 1),
                    period_end=datetime(2024, 9, 30),
                    data={
                        'total_clientes': 3,
                        'novos_clientes': 1,
                        'clientes_ativos': 3,
                        'clientes_inativos': 0,
                        'segmentos': {
                            'Tecnologia': 2,
                            'Consultoria': 1
                        },
                        'localizacao': {
                            'São Paulo': 1,
                            'Rio de Janeiro': 1,
                            'Belo Horizonte': 1
                        }
                    },
                    status='Gerado'
                ),
                Report(
                    title='Performance de Leads - Setembro 2024',
                    type='leads',
                    description='Análise da conversão de leads e origem dos prospects.',
                    generated_by='Carlos Mendes',
                    period_start=datetime(2024, 9, 1),
                    period_end=datetime(2024, 9, 30),
                    data={
                        'total_leads': 2,
                        'leads_qualificados': 1,
                        'taxa_conversao': 50.0,
                        'origem_leads': {
                            'Website': 1,
                            'Indicação': 1
                        },
                        'status_leads': {
                            'Novo': 1,
                            'Qualificado': 1
                        }
                    },
                    status='Gerado'
                )
            ]
            
            db.session.add_all(reports)
            db.session.commit()
            return True
        return False

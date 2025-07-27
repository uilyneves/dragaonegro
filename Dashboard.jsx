import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Users, 
  Calendar, 
  BookOpen, 
  DollarSign, 
  Package, 
  UserCheck,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';

const Dashboard = () => {
  const { user, token, API_BASE } = useAuth();
  const [stats, setStats] = useState({
    totalMembros: 0,
    proximasGiras: 0,
    estoquesBaixos: 0,
    atendimentosPendentes: 0,
    receitaMensal: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Simular dados do dashboard por enquanto
      // Em uma implementação real, faria chamadas para endpoints específicos
      setStats({
        totalMembros: 25,
        proximasGiras: 3,
        estoquesBaixos: 5,
        atendimentosPendentes: 8,
        receitaMensal: 2500.00
      });
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const dashboardCards = [
    {
      title: 'Total de Filhos',
      value: stats.totalMembros,
      description: 'Membros ativos no templo',
      icon: Users,
      color: 'text-blue-400'
    },
    {
      title: 'Próximas Giras',
      value: stats.proximasGiras,
      description: 'Giras agendadas este mês',
      icon: Calendar,
      color: 'text-purple-400'
    },
    {
      title: 'Estoques Baixos',
      value: stats.estoquesBaixos,
      description: 'Itens que precisam reposição',
      icon: Package,
      color: 'text-orange-400'
    },
    {
      title: 'Atendimentos Pendentes',
      value: stats.atendimentosPendentes,
      description: 'Consultas agendadas',
      icon: UserCheck,
      color: 'text-green-400'
    }
  ];

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-red-600/20 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-red-600/20 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Bem-vindo, {user?.nome_ritual}
        </h1>
        <p className="text-red-300">
          Painel de controle do sistema Nzila Dragão
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {dashboardCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <Card key={index} className="bg-black/50 border-red-600">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white">
                  {card.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${card.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">
                  {card.title.includes('Receita') ? `R$ ${card.value.toFixed(2)}` : card.value}
                </div>
                <p className="text-xs text-red-300">
                  {card.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-black/50 border-red-600">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-purple-400" />
              Próximas Giras
            </CardTitle>
            <CardDescription className="text-red-300">
              Giras agendadas para os próximos dias
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-red-600/10 rounded">
                <div>
                  <p className="text-white font-medium">Gira de Desenvolvimento</p>
                  <p className="text-red-300 text-sm">Sexta-feira, 19:00</p>
                </div>
                <span className="text-purple-400 text-sm">Em 2 dias</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-red-600/10 rounded">
                <div>
                  <p className="text-white font-medium">Gira de Consulta</p>
                  <p className="text-red-300 text-sm">Sábado, 20:00</p>
                </div>
                <span className="text-purple-400 text-sm">Em 3 dias</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-red-600">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2 text-orange-400" />
              Alertas do Sistema
            </CardTitle>
            <CardDescription className="text-red-300">
              Itens que precisam de atenção
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center p-3 bg-orange-600/10 rounded">
                <Package className="h-4 w-4 text-orange-400 mr-3" />
                <div>
                  <p className="text-white font-medium">Estoque baixo</p>
                  <p className="text-red-300 text-sm">5 itens precisam reposição</p>
                </div>
              </div>
              <div className="flex items-center p-3 bg-blue-600/10 rounded">
                <UserCheck className="h-4 w-4 text-blue-400 mr-3" />
                <div>
                  <p className="text-white font-medium">Atendimentos pendentes</p>
                  <p className="text-red-300 text-sm">8 consultas agendadas</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Progress */}
      <Card className="bg-black/50 border-red-600">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-green-400" />
            Seu Progresso Ritual
          </CardTitle>
          <CardDescription className="text-red-300">
            Informações sobre sua evolução no caminho iniciático
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-red-600/10 rounded">
              <div className="text-2xl font-bold text-white">{user?.grau}</div>
              <p className="text-red-300 text-sm">Grau Atual</p>
            </div>
            <div className="text-center p-4 bg-red-600/10 rounded">
              <div className="text-2xl font-bold text-white">12</div>
              <p className="text-red-300 text-sm">Giras Participadas</p>
            </div>
            <div className="text-center p-4 bg-red-600/10 rounded">
              <div className="text-2xl font-bold text-white">3</div>
              <p className="text-red-300 text-sm">Provas Vencidas</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;


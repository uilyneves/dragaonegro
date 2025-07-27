import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { 
  Flame, 
  Users, 
  Calendar, 
  BookOpen, 
  DollarSign, 
  Package, 
  UserCheck, 
  Settings, 
  LogOut,
  Crown,
  Star
} from 'lucide-react';

const Sidebar = ({ activeSection, setActiveSection }) => {
  const { user, logout, canAccessGrau, isPaiMaetrono, isTesoureiro } = useAuth();

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Flame,
      grauMinimo: 1
    },
    {
      id: 'membros',
      label: 'Filhos e Iniciados',
      icon: Users,
      grauMinimo: 1
    },
    {
      id: 'giras',
      label: 'Controle de Giras',
      icon: Calendar,
      grauMinimo: 1
    },
    {
      id: 'biblioteca',
      label: 'Biblioteca Doutrinária',
      icon: BookOpen,
      grauMinimo: 1
    },
    {
      id: 'atendimentos',
      label: 'Atendimento Espiritual',
      icon: UserCheck,
      grauMinimo: 3
    },
    {
      id: 'estoque',
      label: 'Estoque Ritualístico',
      icon: Package,
      grauMinimo: 4
    },
    {
      id: 'financeiro',
      label: 'Tesouraria Ritual',
      icon: DollarSign,
      grauMinimo: 1,
      requiresTesoureiro: true
    },
    {
      id: 'configuracoes',
      label: 'Configurações',
      icon: Settings,
      grauMinimo: 6
    }
  ];

  const filteredMenuItems = menuItems.filter(item => {
    if (item.requiresTesoureiro && !isTesoureiro()) return false;
    return canAccessGrau(item.grauMinimo);
  });

  const getGrauIcon = (grau) => {
    if (grau >= 7) return <Crown className="h-4 w-4 text-yellow-400" />;
    if (grau >= 5) return <Star className="h-4 w-4 text-purple-400" />;
    return null;
  };

  return (
    <div className="bg-black border-r border-red-600 h-screen w-64 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-red-600">
        <div className="flex items-center space-x-3">
          <div className="bg-red-600 p-2 rounded-lg">
            <Flame className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg">Nzila Dragão</h1>
            <p className="text-red-300 text-sm">Casa do Dragão Negro</p>
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-red-600">
        <div className="flex items-center space-x-3">
          <div className="bg-red-600 p-2 rounded-full">
            <Users className="h-4 w-4 text-white" />
          </div>
          <div className="flex-1">
            <p className="text-white font-medium text-sm">{user?.nome_ritual}</p>
            <div className="flex items-center space-x-2">
              <p className="text-red-300 text-xs">Grau {user?.grau}</p>
              {getGrauIcon(user?.grau)}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  isActive
                    ? 'bg-red-600 text-white'
                    : 'text-red-200 hover:bg-red-600/20 hover:text-white'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="text-sm">{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-red-600">
        <Button
          onClick={logout}
          variant="ghost"
          className="w-full justify-start text-red-300 hover:text-white hover:bg-red-600/20"
        >
          <LogOut className="h-4 w-4 mr-3" />
          Sair do Sistema
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;


import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Construction } from 'lucide-react';
import './App.css';

// Componente placeholder para seções em desenvolvimento
const ComingSoon = ({ title }) => (
  <div className="p-6">
    <Card className="bg-black/50 border-red-600 max-w-md mx-auto">
      <CardHeader className="text-center">
        <Construction className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-red-300 text-center">
          Este módulo está em desenvolvimento e será disponibilizado em breve.
        </p>
      </CardContent>
    </Card>
  </div>
);

const AppContent = () => {
  const { user, loading } = useAuth();
  const [activeSection, setActiveSection] = useState('dashboard');

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-900 via-black to-red-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-400 mx-auto mb-4"></div>
          <p className="text-white">Carregando sistema...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'membros':
        return <ComingSoon title="Gestão de Filhos e Iniciados" />;
      case 'giras':
        return <ComingSoon title="Controle de Giras" />;
      case 'biblioteca':
        return <ComingSoon title="Biblioteca Doutrinária" />;
      case 'atendimentos':
        return <ComingSoon title="Atendimento Espiritual" />;
      case 'estoque':
        return <ComingSoon title="Estoque Ritualístico" />;
      case 'financeiro':
        return <ComingSoon title="Tesouraria Ritual" />;
      case 'configuracoes':
        return <ComingSoon title="Configurações do Sistema" />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-black to-red-900 flex">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      <main className="flex-1 overflow-auto">
        {renderContent()}
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

